from django.db.utils import OperationalError, ProgrammingError

from .models import ConfiguracionGeneral
from .permissions import es_admin_total, es_docente, es_gestor, obtener_establecimiento_usuario


def info_general(request):
    try:
        config = ConfiguracionGeneral.objects.order_by("id").first()
    except (OperationalError, ProgrammingError):
        config = None

    user_profile_foto_url = ""
    is_docente = False
    is_admin_total_user = False
    is_gestor_user = False
    is_docente_only = False
    establecimiento_gestor = None
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        try:
            perfil = user.perfil
            if perfil and perfil.foto:
                user_profile_foto_url = perfil.foto.url
        except Exception:
            user_profile_foto_url = ""
        is_docente = es_docente(user)
        is_admin_total_user = es_admin_total(user)
        is_gestor_user = es_gestor(user)
        is_docente_only = is_docente and not is_admin_total_user
        establecimiento_gestor = obtener_establecimiento_usuario(user)

    return {
        "info_general": config,
        "user_profile_foto_url": user_profile_foto_url,
        "is_docente": is_docente,
        "is_admin_total": is_admin_total_user,
        "is_gestor": is_gestor_user,
        "is_docente_only": is_docente_only,
        "establecimiento_gestor": establecimiento_gestor,
    }
