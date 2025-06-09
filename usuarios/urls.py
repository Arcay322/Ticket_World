from django.urls import path
from . import views
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('activar/<uidb64>/<token>/', views.activar_cuenta_view, name='activar'),
    path('reenviar-correo-activacion/', views.reenviar_correo_activacion_view, name='reenviar_correo_activacion'),
    path('registro_exitoso/', views.registro_exitoso, name='registro_exitoso'),  
    path('despedida/', views.despedida_view, name='despedida'),
    path('inicio/', views.inicio, name='inicio'),
    path('solicitud_proveedor/', views.solicitud_proveedor, name='solicitud_proveedor'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('admin/solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('admin/solicitudes/aprobar/<int:solicitud_id>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('admin/solicitudes/rechazar/<int:solicitud_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

