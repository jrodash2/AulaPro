from django.urls import path

from . import views

urlpatterns = [
    path('establecimientos/', views.establecimientos_list, name='establecimientos_list'),
    path('establecimientos/<int:est_id>/', views.establecimiento_detail, name='establecimiento_detail'),
    path('establecimientos/<int:est_id>/editar/', views.establecimiento_update, name='establecimiento_update'),

    path('establecimientos/<int:est_id>/ciclos/', views.ciclos_list, name='ciclos_list'),
    path('establecimientos/<int:est_id>/ciclos/nuevo/', views.ciclo_create, name='ciclo_create'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/', views.ciclo_detail, name='ciclo_detail'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/editar/', views.ciclo_update, name='ciclo_update'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/', views.carreras_list, name='carreras_list'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/nuevo/', views.carrera_create, name='carrera_create'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/activar/', views.ciclo_activar, name='ciclo_activar'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/eliminar/', views.ciclo_delete, name='ciclo_delete'),

    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/', views.carrera_detail, name='carrera_detail'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/editar/', views.carrera_update, name='carrera_update'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/grados/', views.grados_list, name='grados_list'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/grados/nuevo/', views.grado_create, name='grado_create'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/grados/<int:grado_id>/', views.grado_detail, name='grado_detail'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/grados/<int:grado_id>/matricula-masiva/', views.matricula_masiva_grado, name='matricula_masiva_grado'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/grados/<int:grado_id>/editar/', views.grado_update, name='grado_update'),

    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/grados/<int:grado_id>/cursos/', views.cursos_list, name='cursos_list'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/grados/<int:grado_id>/cursos/nuevo/', views.curso_create, name='curso_create'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/grados/<int:grado_id>/cursos/<int:curso_id>/editar/', views.curso_update, name='curso_update'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/grados/<int:grado_id>/cursos/<int:curso_id>/asignar-docente/', views.curso_asignar_docente, name='curso_asignar_docente'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/grados/<int:grado_id>/cursos/<int:curso_id>/asignaciones/<int:asignacion_id>/desasignar/', views.curso_desasignar_docente, name='curso_desasignar_docente'),

    path('docente/dashboard/', views.dashboard_docente, name='dashboard_docente'),
    path('docente/mis-cursos/', views.mis_cursos_docente, name='mis_cursos_docente'),
    path('docente/dashboard/legacy/', views.docente_dashboard, name='docente_dashboard'),
    path('docente/cursos/<int:curso_docente_id>/', views.docente_curso_detail, name='docente_curso_detail'),
    path('docente/cursos/<int:curso_docente_id>/asistencia/', views.docente_asistencia_home, name='docente_asistencia_home'),
    path('docente/periodos/<int:periodo_id>/', views.docente_periodo_detail, name='docente_periodo_detail'),
    path('docente/periodos/<int:periodo_id>/tomar-asistencia/', views.tomar_asistencia, name='tomar_asistencia'),
    path('docente/periodos/<int:periodo_id>/historial/', views.docente_historial_asistencias, name='docente_historial_asistencias'),
    path('docente/periodos/<int:periodo_id>/historial/excel/', views.docente_periodo_historial_excel, name='docente_periodo_historial_excel'),
    path('docente/periodos/<int:periodo_id>/eliminar/', views.docente_periodo_delete, name='docente_periodo_delete'),
    path('docente/asistencias/<int:asistencia_id>/', views.docente_asistencia_detail, name='docente_asistencia_detail'),
    path('docente/asistencias/<int:asistencia_id>/excel/', views.docente_asistencia_excel, name='docente_asistencia_excel'),
    path('docente/asistencias/<int:asistencia_id>/pdf/', views.docente_asistencia_excel, name='docente_asistencia_pdf'),
    path('docente/cursos/<int:curso_docente_id>/alumnos/<int:alumno_id>/historial/', views.docente_alumno_historial, name='docente_alumno_historial'),
    path('docente/cursos/<int:curso_docente_id>/alumnos/<int:alumno_id>/historial/excel/', views.docente_alumno_historial_excel, name='docente_alumno_historial_excel'),
    path('docente/cursos/<int:curso_docente_id>/alumnos/<int:alumno_id>/historial/pdf/', views.docente_alumno_historial_excel, name='docente_alumno_historial_pdf'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/grados/<int:grado_id>/buscar-alumno/', views.buscar_alumno, name='buscar_alumno'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/grados/<int:grado_id>/matricular/', views.matricular_alumno, name='matricular_alumno'),
    path('establecimientos/<int:est_id>/ciclos/<int:ciclo_id>/carreras/<int:car_id>/grados/<int:grado_id>/matriculas/<int:matricula_id>/foto/', views.guardar_foto_alumno_grado, name='guardar_foto_alumno_grado'),
    path('matriculas/<int:matricula_id>/desmatricular/', views.desmatricular_alumno, name='desmatricular_alumno'),
]
