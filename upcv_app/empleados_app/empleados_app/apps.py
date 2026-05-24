from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError


class EmpleadosAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'empleados_app'

    def ready(self):
        import empleados_app.signals  # noqa: F401
        try:
            from empleados_app.permissions import asegurar_grupo_gestor

            asegurar_grupo_gestor()
        except (OperationalError, ProgrammingError):
            pass
