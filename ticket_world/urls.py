# ticket_world/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuarios import views as usuarios_views

urlpatterns = [
    path('admin/platform-reports/', include('reports.urls')),
    path('admin/', admin.site.urls),
    

    # Your other app URLs
    path('usuarios/', include('usuarios.urls')),
    path('tickets/', include('tickets.urls')),
    path('', usuarios_views.health_check, name='health_check'), # Apunta a la vista de prueba
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
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]