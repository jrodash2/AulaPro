from django.db.utils import OperationalError, ProgrammingError

from .models import ConfiguracionGeneral


def info_general(request):
    try:
        config = ConfiguracionGeneral.objects.order_by("id").first()
    except (OperationalError, ProgrammingError):
        config = None

    user_profile_foto_url = ""
    is_docente = False
    is_admin_total = False
    is_docente_only = False
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        try:
            perfil = user.perfil
            if perfil and perfil.foto:
                user_profile_foto_url = perfil.foto.url
        except Exception:
            user_profile_foto_url = ""
        is_docente = user.groups.filter(name="Docente").exists()
        is_admin_total = user.is_superuser or user.is_staff or user.groups.filter(name="Administrador").exists() or user.groups.filter(name="Admin_gafetes").exists()
        is_docente_only = is_docente and not is_admin_total

    return {
        "info_general": config,
        "user_profile_foto_url": user_profile_foto_url,
        "is_docente": is_docente,
        "is_admin_total": is_admin_total,
        "is_docente_only": is_docente_only,
    }
