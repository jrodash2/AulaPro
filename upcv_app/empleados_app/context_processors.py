from django.db.utils import OperationalError, ProgrammingError

from .models import ConfiguracionGeneral


def info_general(request):
    try:
        config = ConfiguracionGeneral.objects.order_by("id").first()
    except (OperationalError, ProgrammingError):
        config = None
    return {"info_general": config}
