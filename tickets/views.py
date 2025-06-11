# tickets/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from usuarios.decorators import admin_required # Asumo que admin_required está en esta ruta
from django.db import transaction # <-- ¡Importa transaction para asegurar la atomicidad!

from .models import Evento, Categoria # Modelos optimizados
from .forms import EventoForm, BoletoFormSet # <-- ¡Importa el Formset!


def index(request):
    """
    Vista de bienvenida a la sección de tickets.
    """
    return HttpResponse("¡Bienvenido a la sección de tickets!")

def lista_eventos(request):
    """
    Muestra una lista de todos los eventos.
    Nota: Esta vista podría necesitar filtrado por 'aprobado=True'
    si se usa para el público general, similar a la vista 'inicio' de usuarios.
    """
    eventos = Evento.objects.all().order_by('fecha')
    return render(request, 'tickets/lista_eventos.html', {'eventos': eventos})

def gestion_eventos(request):
    """
    Muestra una página de gestión de eventos.
    """
    eventos = Evento.objects.all().order_by('fecha')
    return render(request, 'tickets/gestion_eventos.html', {'eventos': eventos})


@login_required # Solo usuarios autenticados pueden crear eventos
def crear_evento(request):
    """
    Permite a los proveedores crear un nuevo evento con tipos de boletos asociados.
    El evento se guarda con 'aprobado=False' por defecto.
    """
    # Restricción de rol: Solo proveedores y administradores pueden crear eventos
    if request.user.rol not in ['proveedor', 'admin']:
        messages.error(request, "Solo los proveedores o administradores pueden crear eventos.")
        return redirect('usuarios:inicio') # Redirigir a una página más apropiada

    if request.method == 'POST':
        # Instanciamos el formulario de evento con los datos POST y los archivos (para imagen_portada)
        form = EventoForm(request.POST, request.FILES)
        # Instanciamos el formset de boletos con los datos POST
        formset = BoletoFormSet(request.POST, request.FILES, prefix='boletos')

        if form.is_valid() and formset.is_valid():
            try:
                # Usamos una transacción para asegurar que si falla el guardado de boletos,
                # el evento tampoco se guarde.
                with transaction.atomic():
                    evento = form.save(commit=False)
                    evento.creado_por = request.user # Asigna el usuario que crea el evento
                    evento.aprobado = False # El evento no está aprobado por defecto
                    evento.esta_activo = True # Se considera activo al crearse (visible si se aprueba)
                    evento.save() # Guarda el evento en la base de datos

                    # Guarda los formularios del formset
                    # Los boletos se vincularán automáticamente al evento
                    # save=False es crucial si quieres hacer modificaciones antes de guardar
                    boletos = formset.save(commit=False)
                    for boleto in boletos:
                        boleto.evento = evento # Asegura que el boleto esté vinculado al evento
                        boleto.save()
                    
                    # Manejo de boletos eliminados (si aplica, para edición)
                    formset.save_m2m() # Guarda relaciones ManyToMany si las hubiera (no aplica aquí)

                messages.success(request, f'¡Evento "{evento.nombre}" creado con éxito! Está pendiente de aprobación por el administrador. Se añadieron {len(boletos)} tipos de boletos.')
                return redirect('tickets:lista_eventos') # O a una página de "mis eventos"

            except Exception as e:
                # Si algo sale mal en la transacción, se hace un rollback
                messages.error(request, f'Hubo un error al crear el evento y sus boletos: {e}')
                print(f"Error al crear evento: {e}") # Para depuración
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario y los tipos de boletos.')
            # Los errores del formulario y del formset se mostrarán en la plantilla
    else:
        # Para peticiones GET, instanciamos formularios vacíos
        form = EventoForm()
        formset = BoletoFormSet(prefix='boletos') # Es importante usar el prefix para formsets

    context = {
        'form': form,
        'formset': formset, # Pasamos el formset a la plantilla
        'panel_title': 'Crear Nuevo Evento',
        'panel_subtitle': 'Completa los detalles de tu evento y añade al menos un tipo de boleto. Será revisado por un administrador antes de su publicación.',
    }
    return render(request, 'tickets/crear_evento.html', context)


# --- Vistas de Administración de Eventos (Existentes) ---

@admin_required
def lista_eventos_pendientes(request):
    eventos_pendientes = Evento.objects.filter(aprobado=False).order_by('-fecha')
    context = {
        'eventos': eventos_pendientes,
        'panel_title': 'Eventos Pendientes de Aprobación',
        'panel_subtitle': 'Revisa los eventos creados por los proveedores y decide cuáles se publicarán.'
    }
    return render(request, 'tickets/lista_eventos.html', context)


@admin_required
def aprobar_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    if request.method == 'POST':
        evento.aprobado = True
        evento.save()
        messages.success(request, f'El evento "{evento.nombre}" ha sido aprobado y ahora es visible públicamente.')
        return redirect('tickets:lista_eventos_pendientes')
    messages.error(request, 'Método no permitido para aprobar un evento.')
    return redirect('tickets:lista_eventos_pendientes')


@admin_required
def rechazar_evento(request, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    if request.method == 'POST':
        evento_nombre = evento.nombre
        evento.delete()
        messages.warning(request, f'El evento "{evento_nombre}" ha sido rechazado y eliminado del sistema.')
        return redirect('tickets:lista_eventos_pendientes')
    messages.error(request, 'Método no permitido para rechazar un evento.')
    return redirect('tickets:lista_eventos_pendientes')
