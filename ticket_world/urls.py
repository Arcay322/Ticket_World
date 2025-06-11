# ticket_world/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # <-- ¡IMPORTANTE: Importar settings!
from django.conf.urls.static import static # <-- ¡IMPORTANTE: Importar static!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')), 
    path('tickets/', include('tickets.urls')), 
]

# ESTAS LÍNEAS SON CRUCIALES PARA SERVIR ARCHIVOS MEDIA EN MODO DESARROLLO
# Solo se añaden si DEBUG es True. En producción, se usaría un servidor web (Nginx, Apache).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Si también tienes problemas con CSS/JS que no se cargan,
    # asegúrate de que también tengas:
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
