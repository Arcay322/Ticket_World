# tickets/urls.py
from django.urls import path
from . import views

app_name = 'tickets' # Es buena práctica definir un app_name

urlpatterns = [
    # URLs existentes para eventos públicos y gestión
    path('', views.lista_eventos, name='home'), # AHORA la raíz muestra la lista de eventos
    path('lista/', views.lista_eventos, name='lista_eventos'),
    path('gestion/', views.gestion_eventos, name='gestion_eventos'),
    # path('crear-evento/', views.crear_evento, name='crear_evento'), # Sigue comentada

    # URLs para la gestión de eventos por el administrador (añadidas)
    path('admin/eventos/pendientes/', views.lista_eventos_pendientes, name='lista_eventos_pendientes'),
    path('admin/eventos/aprobar/<int:evento_id>/', views.aprobar_evento, name='aprobar_evento'),
    path('admin/eventos/rechazar/<int:evento_id>/', views.rechazar_evento, name='rechazar_evento'),
    path('crear/', views.crear_evento, name='crear_evento'),
]

