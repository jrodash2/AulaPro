from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from empleados_app.forms import CarreraForm, CicloEscolarForm
from empleados_app.models import Carrera, CicloEscolar, ConfiguracionGeneral, Empleado, Establecimiento, Grado, Matricula

from .forms import MatriculaFiltroForm

ALLOW_MULTI_GRADE_PER_CYCLE = False


def _can_manage(user):
    return user.is_superuser or user.is_staff or user.groups.filter(name="Admin_gafetes").exists()


def _get_establecimiento(est_id):
    return get_object_or_404(Establecimiento, pk=est_id)


def _get_ciclo(est_id, ciclo_id):
    ciclo = get_object_or_404(CicloEscolar.objects.select_related('establecimiento'), pk=ciclo_id)
    if ciclo.establecimiento_id != est_id:
        raise CicloEscolar.DoesNotExist
    return ciclo


def _get_carrera(est_id, ciclo_id, car_id):
    carrera = get_object_or_404(Carrera.objects.select_related('ciclo_escolar', 'ciclo_escolar__establecimiento'), pk=car_id)
    if carrera.ciclo_escolar_id != ciclo_id or carrera.ciclo_escolar.establecimiento_id != est_id:
        raise Carrera.DoesNotExist
    return carrera


def _get_grado(est_id, ciclo_id, car_id, grado_id):
    grado = get_object_or_404(Grado.objects.select_related('carrera', 'carrera__ciclo_escolar', 'carrera__ciclo_escolar__establecimiento'), pk=grado_id)
    if grado.carrera_id != car_id or not grado.carrera or grado.carrera.ciclo_escolar_id != ciclo_id or grado.carrera.ciclo_escolar.establecimiento_id != est_id:
        raise Grado.DoesNotExist
    return grado


@login_required
def establecimientos_list(request):
    establecimientos = Establecimiento.objects.all()
    return render(request, 'aulapro/establecimientos_list.html', {'establecimientos': establecimientos})


@login_required
def establecimiento_detail(request, est_id):
    establecimiento = _get_establecimiento(est_id)
    ciclos = establecimiento.ciclos_escolares.all().order_by('-anio', '-id')
    return render(request, 'aulapro/establecimiento_detail.html', {
        'establecimiento': establecimiento,
        'ciclos': ciclos,
        'ciclo_activo': establecimiento.get_ciclo_activo(),
    })


@login_required
def ciclos_list(request, est_id):
    establecimiento = _get_establecimiento(est_id)
    ciclos = establecimiento.ciclos_escolares.all().order_by('-anio', '-id')
    return render(request, 'aulapro/ciclos_list.html', {
        'establecimiento': establecimiento,
        'ciclos': ciclos,
    })


@login_required
@user_passes_test(_can_manage)
def ciclo_create(request, est_id):
    establecimiento = _get_establecimiento(est_id)
    form = CicloEscolarForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ciclo = form.save(commit=False)
        ciclo.establecimiento = establecimiento
        ciclo.es_activo = bool(form.cleaned_data.get('es_activo'))

        try:
            with transaction.atomic():
                if ciclo.es_activo:
                    establecimiento.ciclos_escolares.filter(es_activo=True).update(es_activo=False)
                ciclo.save()
        except IntegrityError:
            messages.error(request, 'No se pudo crear el ciclo: ya existe un ciclo activo para este establecimiento.')
            return render(request, 'aulapro/ciclos_form.html', {
                'establecimiento': establecimiento,
                'form': form,
                'titulo': 'Nuevo ciclo escolar',
                'accion': 'Guardar ciclo',
            })

        messages.success(request, 'Ciclo escolar creado correctamente.')
        return redirect('empleados:ciclos_list', est_id=establecimiento.id)

    return render(request, 'aulapro/ciclos_form.html', {
        'establecimiento': establecimiento,
        'form': form,
        'titulo': 'Nuevo ciclo escolar',
        'accion': 'Guardar ciclo',
    })


@login_required
@user_passes_test(_can_manage)
def ciclo_update(request, est_id, ciclo_id):
    establecimiento = _get_establecimiento(est_id)
    ciclo = get_object_or_404(CicloEscolar, pk=ciclo_id, establecimiento=establecimiento)
    form = CicloEscolarForm(request.POST or None, instance=ciclo)

    if request.method == 'POST' and form.is_valid():
        ciclo = form.save(commit=False)
        ciclo.establecimiento = establecimiento
        ciclo.es_activo = bool(form.cleaned_data.get('es_activo'))

        try:
            with transaction.atomic():
                if ciclo.es_activo:
                    establecimiento.ciclos_escolares.filter(es_activo=True).exclude(pk=ciclo.pk).update(es_activo=False)
                ciclo.save()
        except IntegrityError:
            messages.error(request, 'No se pudo actualizar: ya existe otro ciclo activo para este establecimiento.')
            return render(request, 'aulapro/ciclos_form.html', {
                'establecimiento': establecimiento,
                'form': form,
                'ciclo': ciclo,
                'titulo': 'Editar ciclo escolar',
                'accion': 'Guardar cambios',
            })

        messages.success(request, 'Ciclo escolar actualizado correctamente.')
        return redirect('empleados:ciclos_list', est_id=establecimiento.id)

    return render(request, 'aulapro/ciclos_form.html', {
        'establecimiento': establecimiento,
        'form': form,
        'ciclo': ciclo,
        'titulo': 'Editar ciclo escolar',
        'accion': 'Guardar cambios',
    })


@login_required
@user_passes_test(_can_manage)
@require_POST
def ciclo_activar(request, est_id, ciclo_id):
    establecimiento = _get_establecimiento(est_id)
    ciclo = get_object_or_404(CicloEscolar, pk=ciclo_id, establecimiento=establecimiento)
    try:
        with transaction.atomic():
            establecimiento.ciclos_escolares.update(es_activo=False)
            ciclo.es_activo = True
            ciclo.estado = 'activo'
            ciclo.save(update_fields=['es_activo', 'estado'])
    except IntegrityError:
        messages.error(request, 'No se pudo activar el ciclo por un conflicto de integridad. Intente nuevamente.')
        return redirect('empleados:ciclos_list', est_id=establecimiento.id)

    messages.success(request, f'El ciclo {ciclo.nombre} ahora está activo.')
    return redirect(request.POST.get('next') or 'empleados:ciclos_list', est_id=establecimiento.id)


@login_required
@user_passes_test(_can_manage)
@require_POST
def ciclo_delete(request, est_id, ciclo_id):
    establecimiento = _get_establecimiento(est_id)
    ciclo = get_object_or_404(CicloEscolar, pk=ciclo_id, establecimiento=establecimiento)

    if ciclo.matriculas.exists():
        messages.warning(request, 'No se puede eliminar el ciclo porque tiene matrículas asociadas.')
        return redirect('empleados:ciclos_list', est_id=establecimiento.id)

    if ciclo.es_activo:
        messages.warning(request, 'No se puede eliminar el ciclo activo. Active otro ciclo primero.')
        return redirect('empleados:ciclos_list', est_id=establecimiento.id)

    ciclo.delete()
    messages.success(request, 'Ciclo escolar eliminado correctamente.')
    return redirect('empleados:ciclos_list', est_id=establecimiento.id)



@login_required
def ciclo_detail(request, est_id, ciclo_id):
    establecimiento = _get_establecimiento(est_id)
    ciclo = _get_ciclo(est_id, ciclo_id)
    carreras = ciclo.carreras.all().order_by('nombre')
    form = CarreraForm(initial={'ciclo_escolar': ciclo, 'activo': True})
    return render(request, 'aulapro/ciclo_detail.html', {
        'establecimiento': establecimiento,
        'ciclo': ciclo,
        'carreras': carreras,
        'form_carrera': form,
    })




@login_required
@user_passes_test(_can_manage)
def carrera_create(request, est_id, ciclo_id):
    ciclo = _get_ciclo(est_id, ciclo_id)
    form = CarreraForm(request.POST or None, initial={'ciclo_escolar': ciclo, 'activo': True})
    if request.method == 'POST' and form.is_valid():
        carrera = form.save(commit=False)
        carrera.ciclo_escolar = ciclo
        carrera.save()
        messages.success(request, 'Carrera creada correctamente.')
        return redirect('empleados:ciclo_detail', est_id=est_id, ciclo_id=ciclo_id)

    return render(request, 'empleados/carrera_form.html', {
        'form': form,
        'titulo': f'Nueva carrera - {ciclo.nombre}',
    })

@login_required
def carrera_detail(request, est_id, ciclo_id, car_id):
    establecimiento = _get_establecimiento(est_id)
    ciclo = _get_ciclo(est_id, ciclo_id)
    carrera = _get_carrera(est_id, ciclo_id, car_id)
    grados = Grado.objects.filter(carrera=carrera).order_by('nombre')
    return render(request, 'aulapro/carrera_detail.html', {
        'establecimiento': establecimiento,
        'ciclo': ciclo,
        'ciclo': ciclo,
        'carrera': carrera,
        'grados': grados,
    })


@login_required
def grado_detail(request, est_id, ciclo_id, car_id, grado_id):
    establecimiento = _get_establecimiento(est_id)
    ciclo = _get_ciclo(est_id, ciclo_id)
    carrera = _get_carrera(est_id, ciclo_id, car_id)
    grado = _get_grado(est_id, car_id, grado_id)

    ciclo_activo = establecimiento.get_ciclo_activo()
    filtro_form = MatriculaFiltroForm(request.GET or None, establecimiento=establecimiento)
    matriculas = Matricula.objects.select_related('alumno', 'ciclo_escolar').filter(grado=grado)

    ciclo_filtrado = None
    if filtro_form.is_valid():
        estado = filtro_form.cleaned_data.get('estado')
        ciclo_filtrado = filtro_form.cleaned_data.get('ciclo_escolar')
        if estado:
            matriculas = matriculas.filter(estado=estado)

    if ciclo_filtrado:
        matriculas = matriculas.filter(ciclo_escolar=ciclo_filtrado)
    elif ciclo_activo:
        matriculas = matriculas.filter(ciclo_escolar=ciclo_activo)

    configuracion = ConfiguracionGeneral.objects.first()
    layout = establecimiento.get_layout()
    orientation = str(layout.get('canvas', {}).get('orientation') or ('V' if (establecimiento.gafete_alto or 0) > (establecimiento.gafete_ancho or 0) else 'H')).upper()
    if orientation not in ('H', 'V'):
        orientation = 'H'
    canvas_width, canvas_height = (1011, 639) if orientation == 'H' else (639, 1011)
    layout['canvas'] = {'width': canvas_width, 'height': canvas_height, 'orientation': orientation}
    return render(request, 'aulapro/grado_detail.html', {
        'establecimiento': establecimiento,
        'ciclo': ciclo,
        'carrera': carrera,
        'grado': grado,
        'matriculas': matriculas.order_by('-created_at', 'alumno__apellidos'),
        'filtro_form': filtro_form,
        'ciclo_activo': ciclo_activo,
        'configuracion': configuracion,
        'layout': layout,
        'canvas_width': canvas_width,
        'canvas_height': canvas_height,
    })


@login_required
@require_GET
def buscar_alumno(request, est_id, ciclo_id, car_id, grado_id):
    _get_grado(est_id, ciclo_id, car_id, grado_id)

    codigo = (request.GET.get('codigo') or '').strip()
    if not codigo:
        return JsonResponse({'found': False, 'error': 'Ingrese un código personal.'}, status=400)

    qs = Empleado.objects.filter(codigo_personal__iexact=codigo)
    if not qs.exists():
        qs = Empleado.objects.filter(codigo_personal__icontains=codigo)

    alumno = qs.order_by('apellidos', 'nombres').first()
    if not alumno:
        return JsonResponse({'found': False, 'error': 'Alumno no encontrado.'}, status=404)

    return JsonResponse({
        'found': True,
        'alumno': {
            'id': alumno.id,
            'codigo': alumno.codigo_personal,
            'nombres': alumno.nombres,
            'apellidos': alumno.apellidos,
            'cui': alumno.cui,
        },
    })


@login_required
@user_passes_test(_can_manage)
@require_POST
def matricular_alumno(request, est_id, ciclo_id, car_id, grado_id):
    grado = _get_grado(est_id, ciclo_id, car_id, grado_id)
    if not grado.carrera or not grado.carrera.ciclo_escolar_id:
        return JsonResponse({'ok': False, 'error': 'El grado no tiene establecimiento asociado.'}, status=400)

    establecimiento = grado.carrera.ciclo_escolar.establecimiento
    ciclo_activo = establecimiento.get_ciclo_activo()
    if not ciclo_activo:
        return JsonResponse({'ok': False, 'error': 'No hay ciclo escolar activo en este establecimiento. Activa uno para matricular.'}, status=409)

    alumno_id = (request.POST.get('alumno_id') or '').strip()
    if not alumno_id:
        return JsonResponse({'ok': False, 'error': 'Debe seleccionar un alumno.'}, status=400)

    alumno = Empleado.objects.filter(pk=alumno_id).first()
    if not alumno:
        return JsonResponse({'ok': False, 'error': 'Alumno no encontrado.'}, status=404)

    if not ALLOW_MULTI_GRADE_PER_CYCLE:
        other = Matricula.objects.filter(
            alumno=alumno,
            ciclo_escolar=ciclo_activo,
            grado__carrera__ciclo_escolar__establecimiento=establecimiento,
        ).exclude(grado=grado).exists()
        if other:
            return JsonResponse({'ok': False, 'error': 'El alumno ya está matriculado en otro grado de este establecimiento para el ciclo activo.'}, status=409)

    try:
        matricula, created = Matricula.objects.get_or_create(
            alumno=alumno,
            grado=grado,
            ciclo_escolar=ciclo_activo,
            defaults={
                'estado': 'activo',
                'ciclo': ciclo_activo.anio,
            },
        )
    except IntegrityError:
        return JsonResponse({'ok': False, 'error': 'El alumno ya está matriculado en este grado y ciclo activo.'}, status=409)

    if not created:
        if matricula.estado != 'activo':
            matricula.estado = 'activo'
            matricula.save(update_fields=['estado'])
        return JsonResponse({'ok': False, 'error': 'El alumno ya está matriculado en este grado y ciclo activo.'}, status=409)

    return JsonResponse({'ok': True, 'message': 'Alumno matriculado correctamente.'})


@login_required
@user_passes_test(_can_manage)
@require_POST
def desmatricular_alumno(request, matricula_id):
    matricula = get_object_or_404(Matricula, pk=matricula_id)
    matricula.estado = 'inactivo'
    matricula.save(update_fields=['estado'])
    messages.warning(request, 'Matrícula inactivada.')
    return redirect(request.POST.get('next') or 'empleados:establecimientos_list')
