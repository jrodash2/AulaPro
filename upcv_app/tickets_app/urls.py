
from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
  
    path('tickets_dahsboard/', views.tickets_dahsboard, name='tickets_dahsboard'),  # Corregido el nombre de la ruta
    path('tickets_dahsboard_adm/', views.tickets_dahsboard_adm, name='tickets_dahsboard_adm'),
    path('tickets_abiertos_adm/', views.tickets_abiertos_adm, name='tickets_abiertos_adm'),
    path('tickets_abiertos/', views.tickets_abiertos, name='tickets_abiertos'),
    path('tickets_proceso_adm/', views.tickets_proceso_adm, name='tickets_proceso_adm'),
    path('tickets_proceso/', views.tickets_proceso, name='tickets_proceso'),
    path('tickets_cerrado_adm/', views.tickets_cerrado_adm, name='tickets_cerrado_adm'),
    path('tickets_cerrado/', views.tickets_cerrado, name='tickets_cerrado'),
    path('tickets_pendiente_adm/', views.tickets_pendiente_adm, name='tickets_pendiente_adm'),
    path('tickets_pendiente/', views.tickets_pendiente, name='tickets_pendiente'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('ticket_tec/<int:ticket_id>/', views.ticket_detail_tec, name='ticket_detail_tec'),
    path('ticket/<int:ticket_id>/edit/', views.ticket_update, name='ticket_update'),
    path('ticket/<int:ticket_id>/edit_adm/', views.update_adm, name='update_adm'),
    path('ticket/new/', views.ticket_create, name='ticket_create'),
    path('ticket/new_adm/', views.ticket_create_adm, name='ticket_create_adm'),
    path('crear_oficina/', views.oficina_create, name='oficina_create'),
    path('tipo_equipo/crear/', views.tipo_equipo_create, name='tipo_equipo_create'),
    path('usuario/crear/', views.user_create, name='user_create'),
    path('usuario/eliminar/<int:user_id>/', views.user_delete, name='user_delete'),
    path('manuales/', views.manuales, name='manuales'),
    path('manualesadm/', views.manualesadm, name='manualesadm'),
]