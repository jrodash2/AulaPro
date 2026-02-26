import json
import re

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
from .models import DEFAULT_GAFETE_LAYOUT, Carrera, ConfiguracionGeneral, Empleado, Establecimiento, Grado, Matricula


def _can_manage_design(user):
    return user.is_superuser or user.is_staff or user.groups.filter(name="Admin_gafetes").exists()


def _validate_layout_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Formato inválido")

    layout = payload.get("layout", payload)
    if not isinstance(layout, dict):
        raise ValueError("Layout inválido")

    canvas = layout.get("canvas") or {"width": 880, "height": 565}
    items = layout.get("items")
    if not isinstance(canvas, dict) or not isinstance(items, dict):
        raise ValueError("El layout debe incluir canvas e items")

    allowed_keys = {"nombres", "apellidos", "grado", "grado_descripcion", "sitio_web", "telefono"}
    allowed_align = {"left", "center", "right"}
    allowed_weight = {"400", "700"}

    result = {
        "canvas": {
            "width": max(500, min(1800, int(canvas.get("width") or 880))),
            "height": max(300, min(1200, int(canvas.get("height") or 565))),
        },
        "items": {},
    }

    for key, cfg in items.items():
        if key not in allowed_keys or not isinstance(cfg, dict):
            continue
        color = (cfg.get("color") or "#111111").strip()
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            raise ValueError(f"Color inválido para {key}")
        align = (cfg.get("align") or "left").strip().lower()
        if align not in allowed_align:
            align = "left"
        weight = str(cfg.get("font_weight") or "400")
        if weight not in allowed_weight:
            weight = "400"
        result["items"][key] = {
            "x": int(cfg.get("x") or 0),
            "y": int(cfg.get("y") or 0),
            "font_size": max(10, min(120, int(cfg.get("font_size") or 24))),
            "font_weight": weight,
            "color": color,
            "align": align,
            "visible": bool(cfg.get("visible", True)),
        }

    if not result["items"]:
        raise ValueError("No se recibieron items válidos")
    return result



def home(request):
    return render(request, "empleados/login.html")

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
    empleados = Empleado.objects.all().order_by("-created_at")
    return render(request, "empleados/lista_empleados.html", {"empleados": empleados})


@login_required
def credencial_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, "empleados/credencial_empleados.html", {"empleados": empleados})


@login_required
def empleado_detalle(request, id):
    empleado = get_object_or_404(Empleado, id=id)
    configuracion = ConfiguracionGeneral.objects.first()
    matricula_activa = empleado.matriculas.filter(estado="activo").select_related("grado", "grado__carrera", "grado__carrera__establecimiento").first()
    establecimiento = None
    grado_gafete = None
    if matricula_activa and matricula_activa.grado:
        grado_gafete = matricula_activa.grado
        if matricula_activa.grado.carrera:
            establecimiento = matricula_activa.grado.carrera.establecimiento

    layout = establecimiento.get_layout() if establecimiento else {"canvas": {"width": 880, "height": 565}, "items": {}}
    return render(
        request,
        "empleados/empleado_detalle.html",
        {
            "empleado": empleado,
            "configuracion": configuracion,
            "establecimiento": establecimiento,
            "layout": layout,
            "grado_gafete": grado_gafete,
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
    matricula_demo = (
        Matricula.objects.select_related("alumno", "grado", "grado__carrera", "grado__carrera__establecimiento")
        .filter(grado__carrera__establecimiento=establecimiento, estado="activo")
        .order_by("-created_at")
        .first()
    )
    alumno = matricula_demo.alumno if matricula_demo else Empleado.objects.first()
    grado_demo = matricula_demo.grado if matricula_demo else None
    layout = establecimiento.get_layout()
    configuracion = ConfiguracionGeneral.objects.first()
    return render(
        request,
        "aulapro/establecimiento_gafete_editor.html",
        {
            "establecimiento": establecimiento,
            "alumno": alumno,
            "grado_demo": grado_demo,
            "layout": layout,
            "layout_json": json.dumps(layout),
            "default_layout_json": json.dumps(DEFAULT_GAFETE_LAYOUT),
            "configuracion": configuracion,
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
    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
        return JsonResponse({"ok": True})
    messages.success(request, "Diseño guardado correctamente.")
    return redirect("empleados:editor_gafete", establecimiento_id=establecimiento.id)


@login_required
@user_passes_test(_can_manage_design)
def resetear_diseno_gafete(request, establecimiento_id):
    establecimiento = get_object_or_404(Establecimiento, pk=establecimiento_id)
    establecimiento.gafete_layout_json = {}
    establecimiento.save(update_fields=["gafete_layout_json"])
    messages.success(request, "Diseño restablecido al valor original.")
    return redirect("empleados:editor_gafete", establecimiento_id=establecimiento.id)
