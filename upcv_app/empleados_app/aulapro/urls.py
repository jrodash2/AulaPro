from django.urls import path

from . import views

urlpatterns = [
    path('establecimientos/', views.establecimientos_list, name='establecimientos_list'),
    path('establecimientos/<int:est_id>/', views.establecimiento_detail, name='establecimiento_detail'),
    path('establecimientos/<int:est_id>/carreras/<int:car_id>/', views.carrera_detail, name='carrera_detail'),
    path('establecimientos/<int:est_id>/carreras/<int:car_id>/grados/<int:grado_id>/', views.grado_detail, name='grado_detail'),
    path(
        'establecimientos/<int:est_id>/carreras/<int:car_id>/grados/<int:grado_id>/matricular/',
        views.grado_matricular,
        name='grado_matricular',
    ),

    # Compatibilidad de endpoints JSON existentes.
    path('grados/<int:grado_id>/buscar-alumno/', views.buscar_alumno, name='buscar_alumno'),
    path('grados/<int:grado_id>/matricular/', views.matricular_alumno, name='matricular_alumno'),
    path('matriculas/<int:matricula_id>/desmatricular/', views.desmatricular_alumno, name='desmatricular_alumno'),
]
