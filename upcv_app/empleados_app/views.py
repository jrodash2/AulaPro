import json

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    CarreraForm,
    ConfiguracionGeneralForm,
    EmpleadoEditForm,
    EmpleadoForm,
    EstablecimientoForm,
    GradoForm,
    MatriculaForm,
)
from .models import Carrera, ConfiguracionGeneral, Empleado, Establecimiento, Grado, Matricula


def _can_manage_design(user):
    return user.is_superuser or user.groups.filter(name="Admin_gafetes").exists()


def _validate_layout_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Formato inválido")
    layers = payload.get("layers")
    if not isinstance(layers, dict):
        raise ValueError("El layout debe incluir layers")
    allowed = {"nombres", "apellidos", "grado", "grado_descripcion", "sitio_web", "telefono"}
    result = {"background": payload.get("background", ""), "layers": {}}
    for key, cfg in layers.items():
        if key not in allowed or not isinstance(cfg, dict):
            continue
        klass = cfg.get("class", "")
        if not isinstance(klass, str):
            klass = ""
        result["layers"][key] = {"class": klass[:20]}
    return result


def home(request):
    return render(request, "empleados/login.html")


def signin(request):
    if request.method == "GET":
        return render(request, "empleados/login.html", {"form": AuthenticationForm})

    user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
    if user is None:
        return render(request, "empleados/login.html", {"form": AuthenticationForm, "error": "Usuario o Password es Incorrecto"})

    auth_login(request, user)
    return redirect("empleados:dahsboard")


def signout(request):
    logout(request)
    return redirect("empleados:signin")


@login_required
def dahsboard(request):
    return render(request, "empleados/dahsboard.html")


@login_required
def configuracion_general(request):
    configuracion, _ = ConfiguracionGeneral.objects.get_or_create(id=1)
    form = ConfiguracionGeneralForm(request.POST or None, request.FILES or None, instance=configuracion)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Configuración actualizada.")
        return redirect("empleados:configuracion_general")
    return render(request, "empleados/configuracion_general.html", {"form": form, "configuracion": configuracion})


@login_required
def crear_empleado(request):
    form = EmpleadoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        empleado = form.save(commit=False)
        empleado.user = request.user
        empleado.save()
        messages.success(request, "Alumno creado correctamente.")
        return redirect("empleados:empleado_lista")
    return render(request, "empleados/crear_empleado.html", {"form": form, "grados": Grado.objects.all()})


@login_required
def editar_empleado(request, e_id):
    empleado = get_object_or_404(Empleado, pk=e_id)
    form = EmpleadoEditForm(request.POST or None, request.FILES or None, instance=empleado)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Alumno actualizado correctamente.")
        return redirect("empleados:empleado_lista")
    return render(request, "empleados/editar_empleado.html", {"form": form, "grados": Grado.objects.all(), "empleado": empleado})


@login_required
def lista_empleados(request):
    empleados = Empleado.objects.select_related("grado", "establecimiento").all().order_by("-created_at", "-grado")
    return render(request, "empleados/lista_empleados.html", {"empleados": empleados})


@login_required
def credencial_empleados(request):
    empleados = Empleado.objects.select_related("grado", "establecimiento").all()
    return render(request, "empleados/credencial_empleados.html", {"empleados": empleados})


@login_required
def empleado_detalle(request, id):
    empleado = get_object_or_404(Empleado, id=id)
    configuracion = ConfiguracionGeneral.objects.first()
    establecimiento = empleado.establecimiento
    matricula_activa = empleado.matriculas.filter(estado="activo").select_related("grado", "grado__carrera").first()
    if not establecimiento and matricula_activa and matricula_activa.grado and matricula_activa.grado.carrera:
        establecimiento = matricula_activa.grado.carrera.establecimiento

    layout = establecimiento.get_layout() if establecimiento else {"background": "", "layers": {}}
    return render(
        request,
        "empleados/empleado_detalle.html",
        {
            "empleado": empleado,
            "configuracion": configuracion,
            "establecimiento": establecimiento,
            "layout": layout,
        },
    )


@login_required
def lista_establecimientos(request):
    establecimientos = Establecimiento.objects.all()
    return render(request, "empleados/establecimiento_lista.html", {"establecimientos": establecimientos})


@login_required
@user_passes_test(_can_manage_design)
def crear_establecimiento(request):
    form = EstablecimientoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Establecimiento creado.")
        return redirect("empleados:establecimiento_lista")
    return render(request, "empleados/establecimiento_form.html", {"form": form, "titulo": "Crear establecimiento"})


@login_required
@user_passes_test(_can_manage_design)
def editar_establecimiento(request, pk):
    establecimiento = get_object_or_404(Establecimiento, pk=pk)
    form = EstablecimientoForm(request.POST or None, request.FILES or None, instance=establecimiento)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Establecimiento actualizado.")
        return redirect("empleados:establecimiento_lista")
    return render(request, "empleados/establecimiento_form.html", {"form": form, "titulo": "Editar establecimiento", "establecimiento": establecimiento})


@login_required
def lista_carreras(request):
    carreras = Carrera.objects.select_related("establecimiento")
    return render(request, "empleados/carrera_lista.html", {"carreras": carreras})


@login_required
def crear_carrera(request):
    form = CarreraForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Carrera creada.")
        return redirect("empleados:carrera_lista")
    return render(request, "empleados/carrera_form.html", {"form": form, "titulo": "Crear carrera"})


@login_required
def editar_carrera(request, pk):
    carrera = get_object_or_404(Carrera, pk=pk)
    form = CarreraForm(request.POST or None, instance=carrera)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Carrera actualizada.")
        return redirect("empleados:carrera_lista")
    return render(request, "empleados/carrera_form.html", {"form": form, "titulo": "Editar carrera"})


@login_required
def lista_grados(request):
    grados = Grado.objects.select_related("carrera", "carrera__establecimiento")
    return render(request, "empleados/grado_lista.html", {"grados": grados})


@login_required
def crear_grado(request):
    form = GradoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Grado creado.")
        return redirect("empleados:grado_lista")
    return render(request, "empleados/grado_form.html", {"form": form, "titulo": "Crear grado"})


@login_required
def editar_grado(request, pk):
    grado = get_object_or_404(Grado, pk=pk)
    form = GradoForm(request.POST or None, instance=grado)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Grado actualizado.")
        return redirect("empleados:grado_lista")
    return render(request, "empleados/grado_form.html", {"form": form, "titulo": "Editar grado"})


@login_required
def matricula_view(request):
    establecimiento_id = request.GET.get("establecimiento") or request.POST.get("establecimiento")
    carrera_id = request.GET.get("carrera") or request.POST.get("carrera")

    form = MatriculaForm(request.POST or None, establecimiento_id=establecimiento_id, carrera_id=carrera_id)
    if request.method == "POST" and form.is_valid():
        matricula = form.save()
        if not matricula.alumno.establecimiento and matricula.grado.carrera and matricula.grado.carrera.establecimiento:
            matricula.alumno.establecimiento = matricula.grado.carrera.establecimiento
            matricula.alumno.save(update_fields=["establecimiento"])
        messages.success(request, "Matrícula registrada.")
        return redirect("empleados:matricula")

    matriculas = Matricula.objects.select_related("alumno", "grado", "grado__carrera", "grado__carrera__establecimiento")
    grado_id = request.GET.get("grado")
    ciclo = request.GET.get("ciclo")
    ciclo_escolar_id = request.GET.get("ciclo_escolar")
    estado = request.GET.get("estado")
    if establecimiento_id:
        matriculas = matriculas.filter(grado__carrera__establecimiento_id=establecimiento_id)
    if carrera_id:
        matriculas = matriculas.filter(grado__carrera_id=carrera_id)
    if grado_id:
        matriculas = matriculas.filter(grado_id=grado_id)
    if ciclo_escolar_id:
        matriculas = matriculas.filter(ciclo_escolar_id=ciclo_escolar_id)
    elif ciclo:
        matriculas = matriculas.filter(ciclo=ciclo)
    if estado:
        matriculas = matriculas.filter(estado=estado)

    establecimientos = Establecimiento.objects.filter(activo=True)
    carreras = Carrera.objects.filter(establecimiento_id=establecimiento_id, activo=True) if establecimiento_id else Carrera.objects.none()
    grados = Grado.objects.filter(carrera_id=carrera_id, activo=True) if carrera_id else Grado.objects.none()

    return render(
        request,
        "empleados/matricula.html",
        {
            "form": form,
            "matriculas": matriculas,
            "establecimientos": establecimientos,
            "carreras": carreras,
            "grados": grados,
        },
    )


@login_required
@user_passes_test(_can_manage_design)
def editor_gafete(request, establecimiento_id):
    establecimiento = get_object_or_404(Establecimiento, pk=establecimiento_id)
    alumno = Empleado.objects.filter(establecimiento=establecimiento).first() or Empleado.objects.first()
    layout = establecimiento.get_layout()
    return render(
        request,
        "empleados/editor_gafete.html",
        {
            "establecimiento": establecimiento,
            "alumno": alumno,
            "layout": json.dumps(layout),
            "layout_preview": layout,
        },
    )


@login_required
@user_passes_test(_can_manage_design)
@require_POST
def guardar_diseno_gafete(request, establecimiento_id):
    establecimiento = get_object_or_404(Establecimiento, pk=establecimiento_id)
    try:
        payload = json.loads(request.body.decode("utf-8"))
        layout = _validate_layout_payload(payload)
    except (ValueError, json.JSONDecodeError, TypeError) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    establecimiento.gafete_layout_json = layout
    establecimiento.save(update_fields=["gafete_layout_json"])
    return JsonResponse({"ok": True})


@login_required
@user_passes_test(_can_manage_design)
def resetear_diseno_gafete(request, establecimiento_id):
    establecimiento = get_object_or_404(Establecimiento, pk=establecimiento_id)
    establecimiento.gafete_layout_json = {}
    establecimiento.save(update_fields=["gafete_layout_json"])
    messages.success(request, "Diseño restablecido al valor original.")
    return redirect("empleados:editor_gafete", establecimiento_id=establecimiento.id)
