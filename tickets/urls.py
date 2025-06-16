# tickets/urls.py
from django.urls import path
from . import views
from .views import (
    index, 
    lista_eventos,
    # ... otras vistas que ya tenías ...
    panel_proveedor_view, # <-- ¡AÑADE ESTA!
    reporte_ventas_view,
    filtrar_eventos_proveedor_ajax,
)

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
    path('evento/<int:evento_id>/', views.detalle_evento_view, name='detalle_evento'), # Ruta para el detalle del evento
    path('agregar-al-carrito/<int:evento_id>/', views.agregar_al_carrito_view, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito_view, name='ver_carrito'),
    path('checkout/procesar/', views.checkout_procesar_view, name='checkout_procesar'),
    path('compra-exitosa/', views.compra_exitosa_view, name='compra_exitosa'),
    path('eliminar-del-carrito/<int:boleto_id>/', views.eliminar_del_carrito_view, name='eliminar_del_carrito'),
    path('actualizar-carrito/', views.actualizar_carrito_view, name='actualizar_carrito'),
    path('evento/<int:evento_id>/editar/', views.editar_evento_view, name='editar_evento'),
    path('mis-eventos/<int:evento_id>/reporte/', views.reporte_ventas_view, name='reporte_ventas'),
    path('eventos-pasados/', views.lista_eventos_pasados, name='lista_eventos_pasados'),
    path('evento/<int:evento_id>/toggle-favorito/', views.toggle_favorito_view, name='toggle_favorito'), # URL para marcar/desmarcar favoritos
    path('panel-proveedor/', panel_proveedor_view, name='panel_proveedor'),
    path('reporte-ventas/<int:evento_id>/', reporte_ventas_view, name='reporte_ventas'),
    path('panel-proveedor/filtrar-eventos/', filtrar_eventos_proveedor_ajax, name='filtrar_eventos_ajax'),
    path('reporte-ventas/<int:evento_id>/', reporte_ventas_view, name='reporte_ventas'),
]

