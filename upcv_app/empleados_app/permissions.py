from django.contrib.auth.models import Group

from .models import Perfil


ADMIN_GROUPS = ("Administrador", "Admin_gafetes")
GESTOR_GROUP = "Gestor"
DOCENTE_GROUP = "Docente"


def asegurar_grupo_gestor():
    Group.objects.get_or_create(name=GESTOR_GROUP)


def es_docente(user):
    return bool(user and user.is_authenticated and user.groups.filter(name=DOCENTE_GROUP).exists())


def es_admin_total(user):
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.is_staff or user.groups.filter(name__in=ADMIN_GROUPS).exists())
    )


def es_admin(user):
    return es_admin_total(user)


def es_gestor(user):
    return bool(user and user.is_authenticated and user.groups.filter(name=GESTOR_GROUP).exists())


def puede_acceder_backoffice(user):
    return bool(user and user.is_authenticated and not es_docente(user))


def puede_administrar_configuracion(user):
    return es_admin_total(user)


def puede_operar_establecimiento(user):
    return es_admin_total(user) or es_gestor(user)


def obtener_establecimiento_usuario(user):
    if not user or not user.is_authenticated:
        return None
    if es_admin_total(user) or not es_gestor(user):
        return None

    try:
        perfil = Perfil.objects.select_related("establecimiento_gestionado").get(user=user)
    except Perfil.DoesNotExist:
        return None

    return perfil.establecimiento_gestionado


def filtrar_por_establecimiento_usuario(queryset, user, lookup):
    if es_admin_total(user):
        return queryset
    if es_gestor(user):
        establecimiento = obtener_establecimiento_usuario(user)
        if not establecimiento:
            return queryset.none()
        return queryset.filter(**{lookup: establecimiento.id})
    return queryset


def usuario_puede_ver_establecimiento(user, establecimiento_id):
    if es_admin_total(user):
        return True
    if es_gestor(user):
        establecimiento = obtener_establecimiento_usuario(user)
        return bool(establecimiento and establecimiento.id == int(establecimiento_id))
    return False
