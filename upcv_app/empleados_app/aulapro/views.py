from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from empleados_app.models import Carrera, Empleado, Establecimiento, Grado, Matricula

from .forms import MatricularPorCodigoForm, MatriculaFiltroForm

ALLOW_MULTI_GRADE_PER_YEAR = False


ESTADOS_MATRICULA = {'activo', 'inactivo'}


def _can_manage(user):
    return user.is_superuser or user.groups.filter(name="Admin_gafetes").exists()


def _get_establecimiento(est_id):
    return get_object_or_404(Establecimiento, pk=est_id)


def _get_carrera(est_id, car_id):
    carrera = get_object_or_404(Carrera.objects.select_related('establecimiento'), pk=car_id)
    if carrera.establecimiento_id != est_id:
        raise Carrera.DoesNotExist
    return carrera


def _get_grado(est_id, car_id, grado_id):
    grado = get_object_or_404(Grado.objects.select_related('carrera', 'carrera__establecimiento'), pk=grado_id)
    if grado.carrera_id != car_id or not grado.carrera or grado.carrera.establecimiento_id != est_id:
        raise Grado.DoesNotExist
    return grado


@login_required
def establecimientos_list(request):
    establecimientos = Establecimiento.objects.all()
    return render(request, 'aulapro/establecimientos_list.html', {'establecimientos': establecimientos})


@login_required
def establecimiento_detail(request, est_id):
    establecimiento = _get_establecimiento(est_id)
    carreras = establecimiento.carreras.all().order_by('nombre')
    return render(request, 'aulapro/establecimiento_detail.html', {
        'establecimiento': establecimiento,
        'carreras': carreras,
    })


@login_required
def carrera_detail(request, est_id, car_id):
    establecimiento = _get_establecimiento(est_id)
    carrera = _get_carrera(est_id, car_id)
    grados = Grado.objects.filter(carrera=carrera).order_by('nombre')
    return render(request, 'aulapro/carrera_detail.html', {
        'establecimiento': establecimiento,
        'carrera': carrera,
        'grados': grados,
    })


@login_required
def grado_detail(request, est_id, car_id, grado_id):
    establecimiento = _get_establecimiento(est_id)
    carrera = _get_carrera(est_id, car_id)
    grado = _get_grado(est_id, car_id, grado_id)

    filtro_form = MatriculaFiltroForm(request.GET or None)
    matriculas = Matricula.objects.select_related('alumno').filter(grado=grado)
    if filtro_form.is_valid():
        ciclo = filtro_form.cleaned_data.get('ciclo')
        estado = filtro_form.cleaned_data.get('estado')
        if ciclo:
            matriculas = matriculas.filter(ciclo=ciclo)
        if estado:
            matriculas = matriculas.filter(estado=estado)

    codigo_personal = (request.GET.get('codigo_personal') or '').strip()
    ciclo_matricula_raw = (request.GET.get('ciclo_matricula') or '').strip()
    estado_matricula = (request.GET.get('estado_matricula') or 'activo').strip().lower()

    try:
        ciclo_matricula = int(ciclo_matricula_raw) if ciclo_matricula_raw else date.today().year
    except ValueError:
        ciclo_matricula = date.today().year

    if estado_matricula not in ESTADOS_MATRICULA:
        estado_matricula = 'activo'

    alumno_encontrado = None
    if codigo_personal:
        alumno_encontrado = Empleado.objects.filter(codigo_personal__iexact=codigo_personal).first()
        if not alumno_encontrado:
            alumno_encontrado = Empleado.objects.filter(codigo_personal__icontains=codigo_personal).order_by('apellidos', 'nombres').first()


    return render(request, 'aulapro/grado_detail.html', {
        'establecimiento': establecimiento,
        'carrera': carrera,
        'grado': grado,
        'matriculas': matriculas.order_by('-ciclo', 'alumno__apellidos'),
        'filtro_form': filtro_form,
        'codigo_personal': codigo_personal,
        'ciclo_matricula': ciclo_matricula,
        'estado_matricula': estado_matricula,
        'alumno_encontrado': alumno_encontrado,
    })


@login_required
@user_passes_test(_can_manage)
@require_POST
def grado_matricular(request, est_id, car_id, grado_id):
    grado = _get_grado(est_id, car_id, grado_id)

    alumno_id = (request.POST.get('alumno_id') or '').strip()
    ciclo_raw = (request.POST.get('ciclo') or '').strip()
    estado = (request.POST.get('estado') or 'activo').strip().lower()

    if not alumno_id or not ciclo_raw:
        messages.error(request, 'Formulario inválido: faltan datos para matricular.')
        return redirect('empleados:grado_detail', est_id=est_id, car_id=car_id, grado_id=grado_id)

    try:
        ciclo = int(ciclo_raw)
    except ValueError:
        messages.error(request, 'El ciclo debe ser un número válido.')
        return redirect('empleados:grado_detail', est_id=est_id, car_id=car_id, grado_id=grado_id)

    if estado not in ESTADOS_MATRICULA:
        estado = 'activo'

    alumno = Empleado.objects.filter(pk=alumno_id).first()
    if not alumno:
        messages.error(request, 'No se encontró el alumno seleccionado.')
        return redirect('empleados:grado_detail', est_id=est_id, car_id=car_id, grado_id=grado_id)

    if not ALLOW_MULTI_GRADE_PER_YEAR:
        other = Matricula.objects.filter(alumno=alumno, ciclo=ciclo).exclude(grado=grado).exists()
        if other:
            messages.warning(request, 'El alumno ya está matriculado en otro grado para este ciclo.')
            return redirect('empleados:grado_detail', est_id=est_id, car_id=car_id, grado_id=grado_id)

    try:
        matricula, created = Matricula.objects.get_or_create(
            alumno=alumno,
            grado=grado,
            ciclo=ciclo,
            defaults={'estado': estado},
        )
    except IntegrityError:
        messages.warning(request, 'El alumno ya está matriculado en este grado y ciclo.')
        return redirect('empleados:grado_detail', est_id=est_id, car_id=car_id, grado_id=grado_id)

    if not created:
        if matricula.estado != estado:
            matricula.estado = estado
            matricula.save(update_fields=['estado'])
        messages.warning(request, 'El alumno ya estaba matriculado en este grado y ciclo.')
        return redirect('empleados:grado_detail', est_id=est_id, car_id=car_id, grado_id=grado_id)

    messages.success(request, 'Alumno matriculado correctamente.')
    return redirect('empleados:grado_detail', est_id=est_id, car_id=car_id, grado_id=grado_id)


@login_required
@require_GET
def buscar_alumno(request, grado_id):
    # Validar grado para no exponer búsquedas fuera de contexto.
    get_object_or_404(Grado, pk=grado_id)

    codigo = (request.GET.get('codigo') or '').strip()
    if not codigo:
        return JsonResponse({'ok': False, 'error': 'Ingrese un código.'}, status=400)

    qs = Empleado.objects.filter(codigo_personal__iexact=codigo)
    if not qs.exists():
        qs = Empleado.objects.filter(codigo_personal__icontains=codigo)

    alumno = qs.order_by('apellidos', 'nombres').first()
    if not alumno:
        return JsonResponse({'ok': False, 'error': 'Alumno no encontrado.'}, status=404)

    return JsonResponse({
        'ok': True,
        'alumno': {
            'id': alumno.id,
            'codigo': alumno.codigo_personal,
            'nombres': alumno.nombres,
            'apellidos': alumno.apellidos,
            'cui': alumno.cui,
        }
    })


@login_required
@user_passes_test(_can_manage)
@require_POST
def matricular_alumno(request, grado_id):
    grado = get_object_or_404(Grado.objects.select_related('carrera', 'carrera__establecimiento'), pk=grado_id)
    form = MatricularPorCodigoForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'error': 'Formulario inválido.'}, status=400)

    codigo = form.cleaned_data['codigo_personal'].strip()
    ciclo = form.cleaned_data['ciclo']
    estado = form.cleaned_data['estado']

    alumno = Empleado.objects.filter(codigo_personal__iexact=codigo).first()
    if not alumno:
        return JsonResponse({'ok': False, 'error': 'Alumno no encontrado.'}, status=404)

    if not ALLOW_MULTI_GRADE_PER_YEAR:
        other = Matricula.objects.filter(alumno=alumno, ciclo=ciclo).exclude(grado=grado).exists()
        if other:
            return JsonResponse({'ok': False, 'error': 'El alumno ya está matriculado en otro grado para este ciclo.'}, status=409)

    try:
        matricula, created = Matricula.objects.get_or_create(
            alumno=alumno,
            grado=grado,
            ciclo=ciclo,
            defaults={'estado': estado},
        )
        if not created and matricula.estado != estado:
            matricula.estado = estado
            matricula.save(update_fields=['estado'])
    except IntegrityError:
        return JsonResponse({'ok': False, 'error': 'El alumno ya está matriculado en este grado y ciclo.'}, status=409)

    return JsonResponse({'ok': True, 'created': created})


@login_required
@user_passes_test(_can_manage)
@require_POST
def desmatricular_alumno(request, matricula_id):
    matricula = get_object_or_404(Matricula, pk=matricula_id)
    matricula.estado = 'inactivo'
    matricula.save(update_fields=['estado'])
    messages.warning(request, 'Matrícula inactivada.')
    return redirect(request.POST.get('next') or 'empleados:establecimientos_list')
