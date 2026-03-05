from django.db.utils import OperationalError, ProgrammingError

from .models import ConfiguracionGeneral


def info_general(request):
    try:
        config = ConfiguracionGeneral.objects.order_by("id").first()
    except (OperationalError, ProgrammingError):
        config = None

    user_profile_foto_url = ""
    is_docente = False
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        try:
            perfil = user.perfil
            if perfil and perfil.foto:
                user_profile_foto_url = perfil.foto.url
        except Exception:
            user_profile_foto_url = ""
        is_docente = user.groups.filter(name="Docente").exists()

    return {
        "info_general": config,
        "user_profile_foto_url": user_profile_foto_url,
        "is_docente": is_docente,
    }
