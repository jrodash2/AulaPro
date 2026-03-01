from django.urls import include, path

from . import views

app_name = "empleados"

urlpatterns = [

    # Navegación jerárquica AulaPro
    path('', include('empleados_app.aulapro.urls')),
    path("signin/", views.signin, name="signin"),
    path("logout/", views.signout, name="logout"),
    path("dahsboard/", views.dahsboard, name="dahsboard"),
    path("config_general/", views.configuracion_general, name="configuracion_general"),

    path("alumnos/crear/", views.crear_empleado, name="crear_empleado"),
    path("alumnos/lista/", views.lista_empleados, name="empleado_lista"),
    path("alumnos/lista/<int:e_id>/", views.editar_empleado, name="editar_empleado"),
    path("alumnos/credencial/", views.credencial_empleados, name="empleado_credencial"),
    path("alumnos/<int:id>/", views.empleado_detalle, name="empleado_detalle"),

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

    path("matriculas/<int:matricula_id>/gafete.jpg", views.gafete_jpg, name="gafete_jpg"),
    path("matriculas/<int:matricula_id>/gafete_descarga.jpg", views.descargar_gafete_jpg, name="descargar_gafete_jpg"),

    path("establecimientos/<int:establecimiento_id>/gafete/editor/", views.editor_gafete, name="editor_gafete"),
    path("establecimientos/<int:establecimiento_id>/gafete/diseno/guardar/", views.guardar_diseno_gafete, name="guardar_diseno_gafete"),
    path("establecimientos/<int:establecimiento_id>/gafete/diseno/reset/", views.resetear_diseno_gafete, name="resetear_diseno_gafete"),

    # Rutas legacy para compatibilidad
    path("crear/", views.crear_empleado, name="legacy_crear"),
    path("lista/", views.lista_empleados, name="legacy_lista"),
    path("lista/<int:e_id>/", views.editar_empleado, name="legacy_editar"),
    path("credencial/", views.credencial_empleados, name="legacy_credencial"),
    path("empleado/<int:id>/", views.empleado_detalle, name="legacy_detalle"),

    path("", views.home, name="home"),
]
