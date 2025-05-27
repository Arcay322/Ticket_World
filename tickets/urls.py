# tickets/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='tickets_home'),
    path('lista/', views.lista_eventos, name='lista_eventos'),
    path('gestion/', views.gestion_eventos, name='gestion_eventos'),
]
