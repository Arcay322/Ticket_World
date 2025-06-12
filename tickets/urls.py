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
    path('evento/<int:evento_id>/', views.detalle_evento_view, name='detalle_evento'),
    path('agregar-al-carrito/<int:evento_id>/', views.agregar_al_carrito_view, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito_view, name='ver_carrito'),
    path('checkout/procesar/', views.checkout_procesar_view, name='checkout_procesar'),
    path('compra-exitosa/', views.compra_exitosa_view, name='compra_exitosa'),
    path('eliminar-del-carrito/<int:boleto_id>/', views.eliminar_del_carrito_view, name='eliminar_del_carrito'),
    path('actualizar-carrito/', views.actualizar_carrito_view, name='actualizar_carrito'),
    path('mis-eventos/', views.mis_eventos_view, name='mis_eventos'),
]

