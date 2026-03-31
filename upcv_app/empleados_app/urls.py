from django.urls import include, path

from . import views

app_name = "empleados"

urlpatterns = [

    # Navegación jerárquica AulaPro
    path('', include('empleados_app.aulapro.urls')),
    path("signin/", views.signin, name="signin"),
    path("logout/", views.signout, name="logout"),
    path("dahsboard/", views.dahsboard, name="dahsboard"),
    path("establecimientos/<int:establecimiento_id>/dashboard/", views.dashboard_establecimiento, name="dashboard_establecimiento"),
    path("config_general/", views.configuracion_general, name="configuracion_general"),
    path("usuarios/", views.usuarios_list, name="usuarios_list"),
    path("usuarios/nuevo/", views.usuarios_create, name="usuarios_create"),
    path("usuarios/<int:pk>/editar/", views.usuarios_update, name="usuarios_update"),

    path("alumnos/crear/", views.crear_empleado, name="crear_empleado"),
    path("alumnos/lista/", views.lista_empleados, name="empleado_lista"),
    path("alumnos/lista/<int:e_id>/", views.editar_empleado, name="editar_empleado"),
    path("alumnos/credencial/", views.credencial_empleados, name="empleado_credencial"),
    path("alumnos/<int:id>/", views.empleado_detalle, name="empleado_detalle"),
    path("alumnos/<int:id>/boleta-asistencia/", views.empleado_boleta_asistencia, name="empleado_boleta_asistencia"),

    path("establecimientos/", views.lista_establecimientos, name="establecimiento_lista"),
    path("establecimientos/crear/", views.crear_establecimiento, name="crear_establecimiento"),
    path("establecimientos/<int:pk>/editar/", views.editar_establecimiento, name="editar_establecimiento"),



    path("matriculas/<int:matricula_id>/gafete.jpg", views.gafete_jpg, name="gafete_jpg"),
    path("matriculas/<int:matricula_id>/gafete_descarga.jpg", views.descargar_gafete_jpg, name="descargar_gafete_jpg"),
    path("matriculas/<int:matricula_id>/gafete_descarga_frente.jpg", views.descargar_gafete_frente_jpg, name="descargar_gafete_frente_jpg"),
    path("matriculas/<int:matricula_id>/gafete_descarga_reverso.jpg", views.descargar_gafete_reverso_jpg, name="descargar_gafete_reverso_jpg"),
    path("matriculas/masiva/", views.matricula_masiva, name="matricula_masiva"),
    path("matriculas/masiva/buscar/", views.matricula_masiva_buscar_alumnos, name="matricula_masiva_buscar_alumnos"),
    path("academico/carga-masiva/", views.carga_masiva_home, name="carga_masiva_home"),
    path("academico/carga-masiva/alumnos/", views.carga_masiva_import_alumnos, name="carga_masiva_import_alumnos"),
    path("academico/carga-masiva/docentes/", views.carga_masiva_import_docentes, name="carga_masiva_import_docentes"),
    path("academico/carga-masiva/cursos/", views.carga_masiva_import_cursos, name="carga_masiva_import_cursos"),
    path("academico/carga-masiva/asignaciones/", views.carga_masiva_import_asignaciones, name="carga_masiva_import_asignaciones"),
    path("academico/carga-masiva/plantillas/<str:tipo>/", views.carga_masiva_plantilla, name="carga_masiva_plantilla"),

    path("establecimientos/<int:establecimiento_id>/gafete/editor/", views.editor_gafete, name="editor_gafete"),
    path("establecimientos/<int:establecimiento_id>/gafete/diseno/guardar/", views.guardar_diseno_gafete, name="guardar_diseno_gafete"),
    path("establecimientos/<int:establecimiento_id>/gafete/subir-imagen/", views.subir_imagen_gafete, name="subir_imagen_gafete"),
    path("establecimientos/<int:establecimiento_id>/gafete/diseno/reset/", views.resetear_diseno_gafete, name="resetear_diseno_gafete"),

    # Rutas legacy para compatibilidad
    path("crear/", views.crear_empleado, name="legacy_crear"),
    path("lista/", views.lista_empleados, name="legacy_lista"),
    path("lista/<int:e_id>/", views.editar_empleado, name="legacy_editar"),
    path("credencial/", views.credencial_empleados, name="legacy_credencial"),
    path("empleado/<int:id>/", views.empleado_detalle, name="legacy_detalle"),
    path("empleado/<int:id>/boleta-asistencia/", views.empleado_boleta_asistencia, name="legacy_boleta_asistencia"),

    path("", views.home, name="home"),
]
