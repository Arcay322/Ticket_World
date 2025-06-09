# tickets/urls.py
from django.urls import path
from . import views

app_name = 'tickets' 

urlpatterns = [
    # path('', views.index, name='tickets_home'), # Esta era la de bienvenida
    path('', views.lista_eventos, name='home'), # AHORA la raíz muestra la lista de eventos
    path('lista/', views.lista_eventos, name='lista_eventos'),
    path('gestion/', views.gestion_eventos, name='gestion_eventos'),
    # path('crear-evento/', views.crear_evento, name='crear_evento'), # Sigue comentada
]