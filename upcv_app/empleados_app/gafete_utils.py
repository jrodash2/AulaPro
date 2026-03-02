BASE_GAFETE_W = 1011
BASE_GAFETE_H = 639


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
