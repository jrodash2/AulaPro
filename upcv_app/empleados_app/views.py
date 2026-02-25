import json

from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    AlumnoForm,
    CarreraForm,
    ConfiguracionGeneralForm,
    EstablecimientoForm,
    GradoForm,
    MatriculaForm,
)
from .models import Alumno, Carrera, ConfiguracionGeneral, Establecimiento, Grado, Matricula


FONT_CHOICES = {"Arial", "Helvetica", "Verdana", "Tahoma"}
ALIGN_CHOICES = {"left", "center", "right"}


def _is_config_admin(user):
    return user.is_superuser or user.groups.filter(name="Admin_gafetes").exists()


def _validate_capas(capas, ancho, alto):
    if not isinstance(capas, list):
        raise ValueError("El diseño debe ser una lista de capas.")
    sanitized = []
    for capa in capas:
        if not isinstance(capa, dict):
            continue
        key = str(capa.get("key", ""))[:60]
        if not key:
            continue
        x = int(capa.get("x", 0))
        y = int(capa.get("y", 0))
        font_size = int(capa.get("font_size", 18))
        font_family = capa.get("font_family", "Arial")
        font_weight = str(capa.get("font_weight", "600"))[:10]
        color = str(capa.get("color", "#111827"))[:12]
        align = capa.get("align", "left")
        max_width = capa.get("max_width")
        max_width = int(max_width) if max_width else None

        if font_family not in FONT_CHOICES:
            font_family = "Arial"
        if align not in ALIGN_CHOICES:
            align = "left"
        if not color.startswith("#"):
            color = "#111827"
        x = max(0, min(x, ancho))
        y = max(0, min(y, alto))
        font_size = max(10, min(font_size, 96))
        if max_width:
            max_width = max(50, min(max_width, ancho))

        sanitized.append(
            {
                "key": key,
                "x": x,
                "y": y,
                "font_size": font_size,
                "font_family": font_family,
                "font_weight": font_weight,
                "color": color,
                "align": align,
                "max_width": max_width,
            }
        )

    if not sanitized:
        raise ValueError("Debe incluir al menos una capa de texto.")
    return sanitized


def home(request):
    return render(request, "empleados/login.html")


def signin(request):
    if request.method == "GET":
        return render(request, "empleados/login.html", {"form": AuthenticationForm})
    user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
    if user is None:
        return render(request, "empleados/login.html", {"form": AuthenticationForm, "error": "Usuario o contraseña incorrectos."})
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
        messages.success(request, "Configuración guardada.")
        return redirect("empleados:configuracion_general")
    return render(request, "empleados/configuracion_general.html", {"form": form, "configuracion": configuracion})


@login_required
def lista_alumnos(request):
    alumnos = Alumno.objects.select_related("grado", "grado__carrera").order_by("-created_at")
    return render(request, "empleados/lista_alumnos.html", {"alumnos": alumnos})


@login_required
def crear_alumno(request):
    form = AlumnoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        alumno = form.save(commit=False)
        alumno.user = request.user
        alumno.save()
        messages.success(request, "Alumno creado correctamente.")
        return redirect("empleados:alumno_lista")
    return render(request, "empleados/alumno_form.html", {"form": form, "titulo": "Crear alumno"})


@login_required
def editar_alumno(request, e_id):
    alumno = get_object_or_404(Alumno, pk=e_id)
    form = AlumnoForm(request.POST or None, request.FILES or None, instance=alumno)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Alumno actualizado correctamente.")
        return redirect("empleados:alumno_lista")
    return render(request, "empleados/alumno_form.html", {"form": form, "titulo": "Editar alumno"})


@login_required
def alumno_detalle(request, id):
    alumno = get_object_or_404(Alumno, id=id)
    configuracion = ConfiguracionGeneral.objects.first()
    matricula = alumno.matriculas.filter(activo=True).select_related("grado", "grado__carrera", "grado__carrera__establecimiento").first()
    establecimiento = matricula.grado.carrera.establecimiento if matricula and matricula.grado and matricula.grado.carrera else None
    capas = establecimiento.capas_por_defecto() if establecimiento else []
    return render(
        request,
        "empleados/alumno_detalle.html",
        {"alumno": alumno, "configuracion": configuracion, "matricula": matricula, "establecimiento": establecimiento, "capas": json.dumps(capas)},
    )


@login_required
def lista_establecimientos(request):
    return render(request, "empleados/establecimiento_lista.html", {"establecimientos": Establecimiento.objects.all()})


@login_required
@user_passes_test(_is_config_admin)
def crear_establecimiento(request):
    form = EstablecimientoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("empleados:establecimiento_lista")
    return render(request, "empleados/simple_form.html", {"form": form, "titulo": "Crear establecimiento"})


@login_required
@user_passes_test(_is_config_admin)
def editar_establecimiento(request, pk):
    obj = get_object_or_404(Establecimiento, pk=pk)
    form = EstablecimientoForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("empleados:establecimiento_lista")
    return render(request, "empleados/simple_form.html", {"form": form, "titulo": "Editar establecimiento"})


@login_required
def lista_carreras(request):
    carreras = Carrera.objects.select_related("establecimiento")
    return render(request, "empleados/carrera_lista.html", {"carreras": carreras})


@login_required
@user_passes_test(_is_config_admin)
def crear_carrera(request):
    form = CarreraForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("empleados:carrera_lista")
    return render(request, "empleados/simple_form.html", {"form": form, "titulo": "Crear carrera"})


@login_required
@user_passes_test(_is_config_admin)
def editar_carrera(request, pk):
    obj = get_object_or_404(Carrera, pk=pk)
    form = CarreraForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("empleados:carrera_lista")
    return render(request, "empleados/simple_form.html", {"form": form, "titulo": "Editar carrera"})


@login_required
def lista_grados(request):
    grados = Grado.objects.select_related("carrera", "carrera__establecimiento")
    return render(request, "empleados/grado_lista.html", {"grados": grados})


@login_required
@user_passes_test(_is_config_admin)
def crear_grado(request):
    form = GradoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("empleados:grado_lista")
    return render(request, "empleados/simple_form.html", {"form": form, "titulo": "Crear grado"})


@login_required
@user_passes_test(_is_config_admin)
def editar_grado(request, pk):
    obj = get_object_or_404(Grado, pk=pk)
    form = GradoForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("empleados:grado_lista")
    return render(request, "empleados/simple_form.html", {"form": form, "titulo": "Editar grado"})


@login_required
def matricula_view(request):
    establecimiento_id = request.GET.get("establecimiento") or request.POST.get("establecimiento")
    carrera_id = request.GET.get("carrera") or request.POST.get("carrera")
    grado_id = request.GET.get("grado") or request.POST.get("grado")
    ciclo = request.GET.get("ciclo") or request.POST.get("ciclo")
    estado = request.GET.get("estado")

    form = MatriculaForm(request.POST or None, establecimiento_id=establecimiento_id, carrera_id=carrera_id)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("empleados:matricula")

    matriculas = Matricula.objects.select_related("alumno", "grado", "grado__carrera", "grado__carrera__establecimiento")
    if establecimiento_id:
        matriculas = matriculas.filter(grado__carrera__establecimiento_id=establecimiento_id)
    if carrera_id:
        matriculas = matriculas.filter(grado__carrera_id=carrera_id)
    if grado_id:
        matriculas = matriculas.filter(grado_id=grado_id)
    if ciclo:
        matriculas = matriculas.filter(ciclo=ciclo)
    if estado in {"activo", "inactivo"}:
        matriculas = matriculas.filter(activo=(estado == "activo"))

    return render(
        request,
        "empleados/matricula.html",
        {
            "form": form,
            "matriculas": matriculas,
            "establecimientos": Establecimiento.objects.all(),
            "carreras": Carrera.objects.filter(establecimiento_id=establecimiento_id) if establecimiento_id else Carrera.objects.none(),
            "grados": Grado.objects.filter(carrera_id=carrera_id) if carrera_id else Grado.objects.none(),
        },
    )


@login_required
@user_passes_test(_is_config_admin)
def editor_gafete(request, establecimiento_id):
    establecimiento = get_object_or_404(Establecimiento, pk=establecimiento_id)
    ejemplo = Alumno.objects.first()
    return render(
        request,
        "empleados/editor_gafete.html",
        {
            "establecimiento": establecimiento,
            "capas": json.dumps(establecimiento.capas_por_defecto()),
            "ejemplo": ejemplo,
        },
    )


@login_required
@user_passes_test(_is_config_admin)
@require_POST
def guardar_diseno_gafete(request, establecimiento_id):
    establecimiento = get_object_or_404(Establecimiento, pk=establecimiento_id)
    try:
        payload = json.loads(request.body.decode("utf-8"))
        capas = _validate_capas(payload.get("capas", []), establecimiento.gafete_ancho, establecimiento.gafete_alto)
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)

    establecimiento.gafete_capas = capas
    establecimiento.save(update_fields=["gafete_capas"])
    return JsonResponse({"ok": True})


@login_required
@user_passes_test(_is_config_admin)
def resetear_diseno_gafete(request, establecimiento_id):
    establecimiento = get_object_or_404(Establecimiento, pk=establecimiento_id)
    establecimiento.gafete_capas = []
    establecimiento.save(update_fields=["gafete_capas"])
    return redirect("empleados:editor_gafete", establecimiento_id=establecimiento.id)
