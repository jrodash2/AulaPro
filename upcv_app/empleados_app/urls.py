from django.urls import path

from . import views

app_name = "empleados"

urlpatterns = [
    path("signin/", views.signin, name="signin"),
    path("logout/", views.signout, name="logout"),
    path("dahsboard/", views.dahsboard, name="dahsboard"),
    path("config_general/", views.configuracion_general, name="configuracion_general"),
    path("", views.home, name="home"),

    path("alumnos/", views.lista_alumnos, name="alumno_lista"),
    path("alumnos/crear/", views.crear_alumno, name="crear_alumno"),
    path("alumnos/<int:e_id>/editar/", views.editar_alumno, name="editar_alumno"),
    path("alumnos/<int:id>/gafete/", views.alumno_detalle, name="alumno_detalle"),

    path("establecimientos/", views.lista_establecimientos, name="establecimiento_lista"),
    path("establecimientos/crear/", views.crear_establecimiento, name="crear_establecimiento"),
    path("establecimientos/<int:pk>/editar/", views.editar_establecimiento, name="editar_establecimiento"),

    path("carreras/", views.lista_carreras, name="carrera_lista"),
    path("carreras/crear/", views.crear_carrera, name="crear_carrera"),
    path("carreras/<int:pk>/editar/", views.editar_carrera, name="editar_carrera"),

    path("grados/", views.lista_grados, name="grado_lista"),
    path("grados/crear/", views.crear_grado, name="crear_grado"),
    path("grados/<int:pk>/editar/", views.editar_grado, name="editar_grado"),

    path("matricula/", views.matricula_view, name="matricula"),

    path("establecimientos/<int:establecimiento_id>/gafete/editor/", views.editor_gafete, name="editor_gafete"),
    path("establecimientos/<int:establecimiento_id>/gafete/diseno/guardar/", views.guardar_diseno_gafete, name="guardar_diseno_gafete"),
    path("establecimientos/<int:establecimiento_id>/gafete/diseno/reset/", views.resetear_diseno_gafete, name="resetear_diseno_gafete"),

    # alias temporal para no romper rutas antiguas
    path("crear/", views.crear_alumno, name="crear_empleado"),
    path("lista/", views.lista_alumnos, name="empleado_lista"),
    path("lista/<int:e_id>/", views.editar_alumno, name="editar_empleado"),
    path("credencial/", views.lista_alumnos, name="empleado_credencial"),
    path("empleado/<int:id>/", views.alumno_detalle, name="empleado_detalle"),
]
