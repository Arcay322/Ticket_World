# ticket_world/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include(('usuarios.urls', 'usuarios'), namespace='usuarios')),
    
    # -------------------------------------------------------------------
    # CAMBIO AQUÍ: Ahora le decimos a Django que la app 'tickets'
    # manejará tanto la ruta '/tickets/...' como la página de inicio ('').
    # -------------------------------------------------------------------
    path('', include('tickets.urls')),
    # -------------------------------------------------------------------
]