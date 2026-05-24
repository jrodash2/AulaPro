from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError


class EmpleadosAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'empleados_app.empleados_app'

    def ready(self):
        from . import signals  # noqa: F401
        try:
            from .permissions import asegurar_grupo_gestor

            asegurar_grupo_gestor()
        except (OperationalError, ProgrammingError):
            pass
