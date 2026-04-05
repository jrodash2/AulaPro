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
    "texto_libre_1": {"x": 80, "y": 120, "font_size": 24, "font_weight": "400", "color": "#111111", "align": "left", "visible": False, "text": ""},
    "texto_libre_2": {"x": 80, "y": 170, "font_size": 24, "font_weight": "400", "color": "#111111", "align": "left", "visible": False, "text": ""},
    "texto_libre_3": {"x": 80, "y": 220, "font_size": 24, "font_weight": "400", "color": "#111111", "align": "left", "visible": False, "text": ""},
    "image": {"x": 30, "y": 30, "w": 220, "h": 220, "src": "", "object_fit": "contain", "visible": False},
}

DEFAULT_ENABLED_FIELDS = ["photo", "nombres", "apellidos", "codigo_alumno", "grado", "telefono", "establecimiento"]
BACK_VISIBLE_KEYS = {
    "nombres",
    "apellidos",
    "codigo_alumno",
    "grado",
    "grado_descripcion",
    "cui",
    "telefono",
    "establecimiento",
    "sitio_web",
    "texto_libre_1",
    "texto_libre_2",
    "texto_libre_3",
}


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
        if not isinstance(cfg, dict):
            continue
        is_dynamic = str(key).startswith("texto_libre_") or str(key).startswith("image")
        if key in out["items"]:
            out["items"][key].update(cfg)
        elif is_dynamic:
            out["items"][key] = copy.deepcopy(cfg)

    enabled = face.get("enabled_fields")
    if isinstance(enabled, list):
        out["enabled_fields"] = [k for k in enabled if k in out["items"]]

    return out


def is_item_allowed_in_face(face, key):
    target_face = "back" if str(face or "front") == "back" else "front"
    key = str(key or "")
    if key.startswith("texto_libre_") or key.startswith("image"):
        return True
    if key not in DEFAULT_FACE_ITEMS:
        return False
    if target_face == "front":
        return True
    return key in BACK_VISIBLE_KEYS


def is_item_visible_in_face(face_layout, face, key):
    if not is_item_allowed_in_face(face, key):
        return False
    if not isinstance(face_layout, dict):
        return False
    items = face_layout.get("items")
    if not isinstance(items, dict):
        return False
    item_cfg = items.get(key)
    if not isinstance(item_cfg, dict):
        return False
    enabled_fields = face_layout.get("enabled_fields")
    if not isinstance(enabled_fields, list) or key not in enabled_fields:
        return False
    default_cfg = DEFAULT_FACE_ITEMS.get(key, {})
    default_visible = bool(default_cfg.get("visible", True))
    return bool(item_cfg.get("visible", default_visible))


def enforce_face_visibility_rules(face_layout, face):
    if not isinstance(face_layout, dict):
        return _default_face(empty=(str(face or "front") == "back"))
    out = copy.deepcopy(face_layout)
    items = out.get("items")
    if not isinstance(items, dict):
        items = {}
    out["items"] = items
    enabled = out.get("enabled_fields")
    if not isinstance(enabled, list):
        enabled = []
    out["enabled_fields"] = [k for k in enabled if is_item_allowed_in_face(face, k) and k in items]
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
        base["front"] = enforce_face_visibility_rules(base["front"], "front")
        base["back"] = enforce_face_visibility_rules(base["back"], "back")
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
    base["front"] = enforce_face_visibility_rules(base["front"], "front")
    base["back"] = enforce_face_visibility_rules(base["back"], "back")
    return base


def obtener_layout_cara(layout, face='front'):
    normalized = normalizar_layout_gafete(layout)
    target = 'back' if face == 'back' else 'front'
    return enforce_face_visibility_rules(normalized.get(target, _default_face(empty=(target == 'back'))), target)


def serializar_layout_frente_reverso(layout, orientation='H'):
    normalized = normalizar_layout_gafete(layout, orientation=orientation)
    return normalized
