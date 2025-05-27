# tickets/views.py
from django.http import HttpResponse
from tickets.models import Evento
from django.shortcuts import render, redirect

def index(request):
    return HttpResponse("¡Bienvenido a la sección de tickets!")

# Vista para que clientes vean la lista de eventos disponibles
def lista_eventos(request):
    eventos = Evento.objects.all().order_by('fecha')
    return render(request, 'tickets/lista_eventos.html', {'eventos': eventos})

# Vista para que proveedores gestionen sus eventos (por ahora listamos todos)
def gestion_eventos(request):
    eventos = Evento.objects.all().order_by('fecha')
    return render(request, 'tickets/gestion_eventos.html', {'eventos': eventos})