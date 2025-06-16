# usuarios/urls.py

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('activar/<uidb64>/<token>/', views.activar_cuenta_view, name='activar'),
    path('reenviar-activacion/', views.reenviar_activacion_view, name='reenviar_activacion'),
    path('registro_exitoso/', views.registro_exitoso, name='registro_exitoso'),
    path('despedida/', views.despedida_view, name='despedida'),
    path('inicio/', views.inicio, name='inicio'),
    path('solicitud_proveedor/', views.solicitud_proveedor, name='solicitud_proveedor'),
    path('perfil/', views.perfil, name='perfil'),
        # --- URLs del Panel de Administración ---
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'), # <-- ¡NUEVA LÍNEA!
    path('admin/solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('admin/solicitudes/aprobar/<int:solicitud_id>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('admin/solicitudes/rechazar/<int:solicitud_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('mi-perfil/notificaciones/', views.notification_list_view, name='notification_list'),
    path('notificaciones/marcar-leida/', views.mark_notification_as_read_view, name='mark_notification_as_read'),
    path('notificaciones/no-leidas/conteo/', views.get_unread_notifications_count, name='unread_notifications_count'),
]

# Esto es para servir archivos de medios (como fotos de perfil) en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)