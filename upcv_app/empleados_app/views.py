import json
import re
import unicodedata
from io import BytesIO

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, JsonResponse
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


BASE_GAFETE_W = 1011
BASE_GAFETE_H = 639


def _canvas_for_orientation(orientation):
    return (BASE_GAFETE_W, BASE_GAFETE_H) if orientation == "H" else (BASE_GAFETE_H, BASE_GAFETE_W)


def _orientation_for_establecimiento(establecimiento):
    if not establecimiento:
        return "H"
    return "V" if (establecimiento.gafete_alto or 0) > (establecimiento.gafete_ancho or 0) else "H"


def _can_manage_design(user):
    return user.is_superuser or user.is_staff or user.groups.filter(name="Admin_gafetes").exists()


def _validate_layout_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Formato inválido")

    layout = payload.get("layout", payload)
    if not isinstance(layout, dict):
        raise ValueError("Layout inválido")

    canvas = layout.get("canvas") or {}
    items = layout.get("items")
    if not isinstance(items, dict):
        raise ValueError("El layout debe incluir items")

    orientation = str(canvas.get("orientation") or "H").upper()
    if orientation not in {"H", "V"}:
        orientation = "H"
    canvas_width, canvas_height = _canvas_for_orientation(orientation)

    allowed_keys = {"photo", "nombres", "apellidos", "codigo_alumno", "grado", "grado_descripcion", "sitio_web", "telefono", "cui", "establecimiento"}
    allowed_align = {"left", "center", "right"}
    allowed_weight = {"400", "700"}

    enabled_fields = layout.get("enabled_fields")
    if not isinstance(enabled_fields, list):
        enabled_fields = list(DEFAULT_GAFETE_LAYOUT.get("enabled_fields", []))
    enabled_fields = [field for field in enabled_fields if field in allowed_keys]

    result = {
        "canvas": {
            "width": canvas_width,
            "height": canvas_height,
            "orientation": orientation,
        },
        "enabled_fields": enabled_fields,
        "items": {},
    }

    for key, cfg in items.items():
        if key not in allowed_keys or not isinstance(cfg, dict):
            continue

        if key == "photo":
            border_color = (cfg.get("border_color") or "#ffffff").strip()
            if not re.fullmatch(r"#[0-9a-fA-F]{6}", border_color):
                raise ValueError("Color de borde inválido para photo")
            shape = (cfg.get("shape") or "rounded").strip().lower()
            if shape not in {"rounded", "circle"}:
                raise ValueError("Forma inválida para photo")
            result["items"][key] = {
                "x": int(cfg.get("x") or 0),
                "y": int(cfg.get("y") or 0),
                "w": max(40, min(canvas_width, int(cfg.get("w") or 250))),
                "h": max(40, min(canvas_height, int(cfg.get("h") or 350))),
                "shape": shape,
                "radius": max(0, min(200, int(cfg.get("radius") or 20))),
                "border": bool(cfg.get("border", True)),
                "border_width": max(0, min(20, int(cfg.get("border_width") or 4))),
                "border_color": border_color,
                "visible": bool(cfg.get("visible", True)),
            }
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


def _canvas_dimensions(establecimiento, orientation=None):
    orient = orientation or _orientation_for_establecimiento(establecimiento)
    return _canvas_for_orientation(orient)


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
    matricula_activa = empleado.matriculas.filter(estado="activo").select_related("grado", "grado__carrera", "grado__carrera__ciclo_escolar__establecimiento").first()
    establecimiento = None
    grado_gafete = None
    if matricula_activa and matricula_activa.grado:
        grado_gafete = matricula_activa.grado
        if matricula_activa.grado.carrera:
            establecimiento = matricula_activa.grado.carrera.ciclo_escolar.establecimiento

    layout = establecimiento.get_layout() if establecimiento else {"canvas": {"width": 880, "height": 565}, "items": {}}
    orientation = str(layout.get("canvas", {}).get("orientation") or _orientation_for_establecimiento(establecimiento)).upper()
    if orientation not in {"H", "V"}:
        orientation = "H"
    canvas_width, canvas_height = _canvas_dimensions(establecimiento, orientation=orientation)
    layout["canvas"] = {"width": canvas_width, "height": canvas_height, "orientation": orientation}
    if not isinstance(layout.get("enabled_fields"), list):
        layout["enabled_fields"] = list(DEFAULT_GAFETE_LAYOUT.get("enabled_fields", []))
    return render(
        request,
        "empleados/empleado_detalle.html",
        {
            "empleado": empleado,
            "configuracion": configuracion,
            "is_editor": True,
            "establecimiento": establecimiento,
            "layout": layout,
            "grado_gafete": grado_gafete,
            "canvas_width": canvas_width,
            "canvas_height": canvas_height,
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
    carreras = Carrera.objects.select_related("ciclo_escolar", "ciclo_escolar__establecimiento")
    return render(request, "empleados/carrera_lista.html", {"carreras": carreras})


@login_required
def crear_carrera(request):
    ciclo_id = request.GET.get("ciclo_escolar") or request.POST.get("ciclo_escolar")
    initial = {"ciclo_escolar": ciclo_id} if ciclo_id else None
    form = CarreraForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        carrera = form.save()
        messages.success(request, "Carrera creada.")
        return redirect("empleados:ciclo_detail", est_id=carrera.ciclo_escolar.establecimiento_id, ciclo_id=carrera.ciclo_escolar_id)
    return render(request, "empleados/carrera_form.html", {"form": form, "titulo": "Crear carrera"})


@login_required
def editar_carrera(request, pk):
    carrera = get_object_or_404(Carrera, pk=pk)
    form = CarreraForm(request.POST or None, instance=carrera)
    if request.method == "POST" and form.is_valid():
        carrera = form.save()
        messages.success(request, "Carrera actualizada.")
        return redirect("empleados:ciclo_detail", est_id=carrera.ciclo_escolar.establecimiento_id, ciclo_id=carrera.ciclo_escolar_id)
    return render(request, "empleados/carrera_form.html", {"form": form, "titulo": "Editar carrera"})


@login_required
def lista_grados(request):
    grados = Grado.objects.select_related("carrera", "carrera__ciclo_escolar__establecimiento")
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

    matriculas = Matricula.objects.select_related("alumno", "grado", "grado__carrera", "grado__carrera__ciclo_escolar__establecimiento")
    grado_id = request.GET.get("grado")
    ciclo = request.GET.get("ciclo")
    ciclo_escolar_id = request.GET.get("ciclo_escolar")
    estado = request.GET.get("estado")
    if establecimiento_id:
        matriculas = matriculas.filter(grado__carrera__ciclo_escolar__establecimiento_id=establecimiento_id)
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
    carreras = Carrera.objects.filter(ciclo_escolar__establecimiento_id=establecimiento_id, activo=True) if establecimiento_id else Carrera.objects.none()
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
        Matricula.objects.select_related("alumno", "grado", "grado__carrera", "grado__carrera__ciclo_escolar__establecimiento")
        .filter(grado__carrera__ciclo_escolar__establecimiento=establecimiento, estado="activo")
        .order_by("-created_at")
        .first()
    )
    alumno = matricula_demo.alumno if matricula_demo else Empleado.objects.first()
    grado_demo = matricula_demo.grado if matricula_demo else None
    layout = establecimiento.get_layout()
    orientation = str(layout.get("canvas", {}).get("orientation") or _orientation_for_establecimiento(establecimiento)).upper()
    if orientation not in {"H", "V"}:
        orientation = "H"
    canvas_width, canvas_height = _canvas_dimensions(establecimiento, orientation=orientation)
    layout["canvas"] = {"width": canvas_width, "height": canvas_height, "orientation": orientation}
    if not isinstance(layout.get("enabled_fields"), list):
        layout["enabled_fields"] = list(DEFAULT_GAFETE_LAYOUT.get("enabled_fields", []))
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
            "is_editor": True,
            "canvas_width": canvas_width,
            "canvas_height": canvas_height,
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
    orientation = str(layout.get("canvas", {}).get("orientation") or _orientation_for_establecimiento(establecimiento)).upper()
    if orientation not in {"H", "V"}:
        orientation = "H"
    canvas_width, canvas_height = _canvas_dimensions(establecimiento, orientation=orientation)
    layout["canvas"] = {"width": canvas_width, "height": canvas_height, "orientation": orientation}
    if not isinstance(layout.get("enabled_fields"), list):
        layout["enabled_fields"] = list(DEFAULT_GAFETE_LAYOUT.get("enabled_fields", []))
    establecimiento.gafete_ancho = canvas_width
    establecimiento.gafete_alto = canvas_height
    establecimiento.gafete_layout_json = layout
    establecimiento.save(update_fields=["gafete_layout_json", "gafete_ancho", "gafete_alto"])
    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
        return JsonResponse({"ok": True})
    messages.success(request, "Diseño guardado correctamente.")
    return redirect("empleados:editor_gafete", establecimiento_id=establecimiento.id)



def _safe_text(value, fallback="-"):
    text = str(value or "").strip()
    return text if text else fallback


def _sanitize_filename_token(value):
    text = unicodedata.normalize("NFKD", _safe_text(value, fallback=""))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")
    return text or "NA"


def _build_gafete_filename(alumno):
    apellidos = _sanitize_filename_token(getattr(alumno, "apellidos", ""))
    nombres = _sanitize_filename_token(getattr(alumno, "nombres", ""))
    codigo = _sanitize_filename_token(getattr(alumno, "codigo_personal", ""))
    return f"GAFETE_{apellidos}_{nombres}_{codigo}.jpg"


def _parse_color(value, default="#111111"):
    try:
        return ImageColor.getrgb(str(value or default))
    except ValueError:
        return ImageColor.getrgb(default)


def _load_font(font_size=24, bold=False):
    font_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for font_path in font_candidates:
        try:
            return ImageFont.truetype(font_path, max(10, int(font_size or 24)))
        except OSError:
            continue
    return ImageFont.load_default()


def _field_text_for_key(key, matricula, establecimiento):
    alumno = matricula.alumno
    grado = matricula.grado
    mapping = {
        "nombres": _safe_text(getattr(alumno, "nombres", ""), "Nombre"),
        "apellidos": _safe_text(getattr(alumno, "apellidos", ""), "Apellidos"),
        "codigo_alumno": _safe_text(getattr(alumno, "codigo_personal", ""), "-"),
        "grado": _safe_text(getattr(grado, "nombre", ""), "Grado"),
        "grado_descripcion": _safe_text(getattr(grado, "descripcion", ""), ""),
        "sitio_web": _safe_text(getattr(establecimiento, "sitio_web", ""), ""),
        "telefono": _safe_text(getattr(alumno, "tel", ""), "-"),
        "cui": _safe_text(getattr(alumno, "cui", ""), "—"),
        "establecimiento": _safe_text(getattr(establecimiento, "nombre", ""), ""),
    }
    return mapping.get(key, "")


def _render_gafete_jpg_bytes(matricula, establecimiento, layout, canvas_width, canvas_height):
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")

    if establecimiento and establecimiento.background_gafete:
        try:
            with establecimiento.background_gafete.open("rb") as bg_file:
                background = Image.open(bg_file).convert("RGB")
                background = ImageOps.fit(background, (canvas_width, canvas_height), method=Image.Resampling.LANCZOS)
                canvas.paste(background, (0, 0))
        except Exception:
            pass

    items = layout.get("items", {}) if isinstance(layout, dict) else {}
    enabled_fields = set(layout.get("enabled_fields", [])) if isinstance(layout, dict) else set()

    photo_cfg = items.get("photo", {}) if isinstance(items.get("photo", {}), dict) else {}
    if "photo" in enabled_fields and photo_cfg.get("visible", True) and getattr(matricula.alumno, "imagen", None):
        x = int(photo_cfg.get("x", 20))
        y = int(photo_cfg.get("y", 40))
        w = max(20, int(photo_cfg.get("w", 250)))
        h = max(20, int(photo_cfg.get("h", 350)))
        border_width = max(0, int(photo_cfg.get("border_width", 4))) if photo_cfg.get("border", True) else 0
        border_color = _parse_color(photo_cfg.get("border_color", "#ffffff"), default="#ffffff")
        shape = str(photo_cfg.get("shape") or "rounded").lower()
        radius = max(0, int(photo_cfg.get("radius", 20)))

        try:
            with matricula.alumno.imagen.open("rb") as photo_file:
                photo = Image.open(photo_file).convert("RGB")
                photo = ImageOps.fit(photo, (w, h), method=Image.Resampling.LANCZOS)
                alpha_mask = Image.new("L", (w, h), 0)
                alpha_draw = ImageDraw.Draw(alpha_mask)
                if shape == "circle":
                    alpha_draw.ellipse((0, 0, w, h), fill=255)
                else:
                    alpha_draw.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)

                if border_width > 0:
                    border_img = Image.new("RGBA", (w + border_width * 2, h + border_width * 2), (0, 0, 0, 0))
                    border_mask = Image.new("L", border_img.size, 0)
                    border_draw = ImageDraw.Draw(border_mask)
                    if shape == "circle":
                        border_draw.ellipse((0, 0, border_img.size[0], border_img.size[1]), fill=255)
                    else:
                        border_draw.rounded_rectangle(
                            (0, 0, border_img.size[0], border_img.size[1]),
                            radius=radius + border_width,
                            fill=255,
                        )
                    border_fill = Image.new("RGBA", border_img.size, (*border_color, 255))
                    border_img.paste(border_fill, (0, 0), border_mask)
                    canvas.paste(border_img, (x - border_width, y - border_width), border_img)

                photo_rgba = photo.convert("RGBA")
                photo_rgba.putalpha(alpha_mask)
                canvas.paste(photo_rgba, (x, y), photo_rgba)
        except Exception:
            pass

    draw = ImageDraw.Draw(canvas)
    for key, cfg in items.items():
        if key == "photo" or key not in enabled_fields or not isinstance(cfg, dict) or not cfg.get("visible", True):
            continue
        text = _field_text_for_key(key, matricula, establecimiento)
        if not text:
            continue
        x = int(cfg.get("x", 0))
        y = int(cfg.get("y", 0))
        font_size = int(cfg.get("font_size", 24))
        weight = str(cfg.get("font_weight", "400"))
        color = _parse_color(cfg.get("color", "#111111"), default="#111111")
        align = str(cfg.get("align", "left")).lower()
        font = _load_font(font_size=font_size, bold=(weight == "700"))

        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        tx = x
        if align == "center":
            tx = x - text_w // 2
        elif align == "right":
            tx = x - text_w

        draw.text((tx, y), text, fill=color, font=font)

    config = ConfiguracionGeneral.objects.first()
    if config and config.logotipo:
        try:
            with config.logotipo.open("rb") as logo_file:
                logo = Image.open(logo_file).convert("RGBA")
                logo.thumbnail((170, 170), Image.Resampling.LANCZOS)
                canvas.paste(logo, (12, 40), logo)
        except Exception:
            pass

    buffer = BytesIO()
    canvas.save(buffer, format="JPEG", quality=95, optimize=True)
    return buffer.getvalue()


@login_required
def gafete_jpg(request, matricula_id):
    matricula = get_object_or_404(
        Matricula.objects.select_related("alumno", "grado", "grado__carrera", "grado__carrera__ciclo_escolar__establecimiento"),
        pk=matricula_id,
    )
    establecimiento = matricula.grado.carrera.ciclo_escolar.establecimiento if matricula.grado and matricula.grado.carrera else None
    if not establecimiento:
        return HttpResponse("No se encontró establecimiento para la matrícula.", status=404)

    layout = establecimiento.get_layout() if establecimiento else DEFAULT_GAFETE_LAYOUT
    orientation = str(layout.get("canvas", {}).get("orientation") or _orientation_for_establecimiento(establecimiento)).upper()
    if orientation not in {"H", "V"}:
        orientation = "H"
    canvas_width, canvas_height = _canvas_for_orientation(orientation)
    image_bytes = _render_gafete_jpg_bytes(matricula, establecimiento, layout, canvas_width, canvas_height)

    filename = _build_gafete_filename(matricula.alumno)
    response = HttpResponse(image_bytes, content_type="image/jpeg")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
def descargar_gafete_jpg(request, matricula_id):
    return gafete_jpg(request, matricula_id)


@login_required
@user_passes_test(_can_manage_design)
def resetear_diseno_gafete(request, establecimiento_id):
    establecimiento = get_object_or_404(Establecimiento, pk=establecimiento_id)
    establecimiento.gafete_layout_json = {}
    establecimiento.gafete_ancho, establecimiento.gafete_alto = _canvas_for_orientation("H")
    establecimiento.save(update_fields=["gafete_layout_json", "gafete_ancho", "gafete_alto"])
    messages.success(request, "Diseño restablecido al valor original.")
    return redirect("empleados:editor_gafete", establecimiento_id=establecimiento.id)
