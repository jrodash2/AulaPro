from django.urls import path
from . import views

app_name = 'empleados'


urlpatterns = [
    path('crear/', views.crear_empleado, name='crear_empleado'),
    path('signin/', views.signin, name='signin'),
    path('dahsboard/', views.dahsboard, name='dahsboard'), 
    path('config_general/', views.configuracion_general, name='configuracion_general'), 

    path('logout/', views.signout, name='logout',),
    path('lista/', views.lista_empleados, name='empleado_lista'),
    path('lista/<int:e_id>/', views.editar_empleado, name='editar_empleado',),
    path('credencial/', views.credencial_empleados, name='empleado_credencial'),
    path('', views.home, name='home'), 
    path('empleado/<int:id>/', views.empleado_detalle, name='empleado_detalle'),
]
