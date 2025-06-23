# ticket_world/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuarios import views as usuarios_views

urlpatterns = [
    path('admin/platform-reports/', include('reports.urls')),
    path('admin/', admin.site.urls),
    

    # Include reports app URLs under the 'admin' namespace
    # This makes the 'admin:sales_report' URL work as expected
    # ¡IMPORTANTE!: Esta línea debe ser eliminada o comentada
    # ya que la aplicación 'reports' fue eliminada de INSTALLED_APPS
    # path('admin/reports/', include('reports.urls', namespace='admin')), # ELIMINAR O COMENTAR

    # Your other app URLs
    path('usuarios/', include('usuarios.urls')),
    path('tickets/', include('tickets.urls')),
    

]

# These lines are crucial for serving MEDIA and STATIC files in development mode.
# They are only added if DEBUG is True. In production, a web server (Nginx, Apache) would be used.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # It's good practice to also ensure STATIC files are served in development,
    # although `collectstatic` is for production setup.
    # If you have static files directly in your 'static' folder that aren't collected
    # by an app, this line helps.
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)