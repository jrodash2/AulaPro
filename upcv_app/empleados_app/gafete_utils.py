import copy

BASE_GAFETE_W = 1011
BASE_GAFETE_H = 639

DEFAULT_FACE_ITEMS = {
    "photo": {
        "x": 20,
        "y": 40,
        "w": 250,
        "h": 350,
        "shape": "rounded",
        "radius": 20,
        "border": True,
        "border_width": 4,
        "border_color": "#ffffff",
        "visible": True,
    },
    "nombres": {"x": 300, "y": 120, "font_size": 45, "font_weight": "700", "color": "#090909", "align": "left", "visible": True},
    "apellidos": {"x": 300, "y": 180, "font_size": 50, "font_weight": "400", "color": "#111111", "align": "left", "visible": True},
    "codigo_alumno": {"x": 300, "y": 235, "font_size": 22, "font_weight": "700", "color": "#111111", "align": "left", "visible": True},
    "grado": {"x": 350, "y": 260, "font_size": 25, "font_weight": "400", "color": "#090909", "align": "left", "visible": True},
    "grado_descripcion": {"x": 350, "y": 290, "font_size": 25, "font_weight": "400", "color": "#0f0f0f", "align": "left", "visible": True},
    "sitio_web": {"x": 580, "y": 430, "font_size": 28, "font_weight": "400", "color": "#275393", "align": "left", "visible": True},
    "telefono": {"x": 520, "y": 500, "font_size": 35, "font_weight": "700", "color": "#030303", "align": "left", "visible": True},
    "cui": {"x": 300, "y": 330, "font_size": 20, "font_weight": "400", "color": "#111111", "align": "left", "visible": False},
    "establecimiento": {"x": 300, "y": 360, "font_size": 20, "font_weight": "400", "color": "#111111", "align": "left", "visible": True},
    "image": {"x": 30, "y": 30, "w": 220, "h": 220, "src": "", "object_fit": "contain", "visible": False},
}

DEFAULT_ENABLED_FIELDS = ["photo", "nombres", "apellidos", "codigo_alumno", "grado", "telefono", "establecimiento"]


def canvas_for_orientation(orientation):
    orient = str(orientation or 'H').upper()
    return (BASE_GAFETE_W, BASE_GAFETE_H) if orient == 'H' else (BASE_GAFETE_H, BASE_GAFETE_W)


def orientation_for_establecimiento(establecimiento):
    if not establecimiento:
        return 'H'
    return 'V' if (establecimiento.gafete_alto or 0) > (establecimiento.gafete_ancho or 0) else 'H'


def resolve_gafete_dimensions(establecimiento, layout=None):
    orient = orientation_for_establecimiento(establecimiento)
    w, h = canvas_for_orientation(orient)
    return orient, w, h


def _default_face(empty=False):
    items = copy.deepcopy(DEFAULT_FACE_ITEMS)
    if empty:
        for key, cfg in items.items():
            if isinstance(cfg, dict):
                cfg["visible"] = False
        items["image"]["visible"] = False
    return {
        "background_image": "",
        "enabled_fields": [] if empty else list(DEFAULT_ENABLED_FIELDS),
        "items": items,
    }


def default_layout_front_back(orientation='H'):
    w, h = canvas_for_orientation(orientation)
    return {
        "canvas": {"width": w, "height": h, "orientation": orientation},
        "front": _default_face(empty=False),
        "back": _default_face(empty=True),
    }


def _merge_face(face, default_face):
    out = copy.deepcopy(default_face)
    if not isinstance(face, dict):
        return out
    out["background_image"] = str(face.get("background_image") or "")

    incoming_items = face.get("items") if isinstance(face.get("items"), dict) else {}
    for key, cfg in incoming_items.items():
        if key not in out["items"]:
            continue
        if isinstance(cfg, dict):
            out["items"][key].update(cfg)

    enabled = face.get("enabled_fields")
    if isinstance(enabled, list):
        out["enabled_fields"] = [k for k in enabled if k in out["items"]]

    return out


def normalizar_layout_gafete(raw_layout, orientation='H'):
    base = default_layout_front_back(orientation=orientation)
    if not isinstance(raw_layout, dict):
        return base

    canvas = raw_layout.get("canvas") if isinstance(raw_layout.get("canvas"), dict) else {}
    orient = str(canvas.get("orientation") or orientation).upper()
    if orient not in ('H', 'V'):
        orient = orientation
    w, h = canvas_for_orientation(orient)
    base["canvas"] = {"width": w, "height": h, "orientation": orient}

    # Nuevo formato
    if isinstance(raw_layout.get("front"), dict) or isinstance(raw_layout.get("back"), dict):
        base["front"] = _merge_face(raw_layout.get("front"), _default_face(empty=False))
        base["back"] = _merge_face(raw_layout.get("back"), _default_face(empty=True))
        return base

    # Formato legado
    legacy_front = {
        "background_image": str(raw_layout.get("background_image") or ""),
        "enabled_fields": raw_layout.get("enabled_fields", []),
        "items": raw_layout.get("items", {}),
    }
    if isinstance(raw_layout.get("fields"), list) and not legacy_front["items"]:
        converted = {}
        for field in raw_layout["fields"]:
            if not isinstance(field, dict):
                continue
            key = field.get("key")
            if key == "telefono_emergencia":
                key = "telefono"
            if key in DEFAULT_FACE_ITEMS:
                converted[key] = {k: field[k] for k in ["x", "y", "font_size", "font_weight", "color", "align", "visible"] if k in field}
        legacy_front["items"] = converted

    base["front"] = _merge_face(legacy_front, _default_face(empty=False))
    return base


def obtener_layout_cara(layout, face='front'):
    normalized = normalizar_layout_gafete(layout)
    target = 'back' if face == 'back' else 'front'
    return normalized.get(target, _default_face(empty=(target == 'back')))


def serializar_layout_frente_reverso(layout, orientation='H'):
    normalized = normalizar_layout_gafete(layout, orientation=orientation)
    return normalized
