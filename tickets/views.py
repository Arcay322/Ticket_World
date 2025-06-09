# tickets/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse
# from django import forms # Lo dejamos comentado por ahora
# from tickets.forms import EventoForm # Lo dejamos comentado por ahora

# Importamos los modelos necesarios en una sola línea
from tickets.models import Evento, Categoria

def index(request):
    return HttpResponse("¡Bienvenido a la sección de tickets!")

def lista_eventos(request):
    eventos = Evento.objects.all().order_by('fecha')
    return render(request, 'tickets/lista_eventos.html', {'eventos': eventos})

def gestion_eventos(request):
    eventos = Evento.objects.all().order_by('fecha')
    return render(request, 'tickets/gestion_eventos.html', {'eventos': eventos})

# -------------------------------------------------------------------
# SE COMENTA TEMPORALMENTE PARA PODER EJECUTAR LAS MIGRACIONES
# Cuando estés listo para desarrollar esta funcionalidad, puedes descomentarla.
# -------------------------------------------------------------------
# def crear_evento(request):
#     if request.method == "POST":
#         form = EventoForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('lista_eventos')
#     else:
#         form = EventoForm()
#     return render(request, "tickets/crear_evento.html", {"form": form})
# -------------------------------------------------------------------