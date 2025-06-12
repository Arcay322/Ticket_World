# tickets/views.py

# --- Imports ---
import json
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# --- Imports de nuestras aplicaciones ---
from usuarios.decorators import admin_required
from .models import Evento, Categoria, Boleto, Venta, DetalleVenta, MetodoPago
from .forms import EventoForm, BoletoFormSetCreate, BoletoFormSetEdit
from django.template.loader import render_to_string 
from django.core.mail import EmailMultiAlternatives 

# ======================================================
# === Vistas Públicas Generales
# ======================================================

def index(request):
    """
    Vista de bienvenida a la sección de tickets (si se usa).
    """
    return HttpResponse("¡Bienvenido a la sección de tickets!")


def lista_eventos(request):
    """
    Muestra una lista PÚBLICA de todos los eventos APROBADOS y futuros.
    """
    eventos_publicos = Evento.objects.filter(aprobado=True, fecha__gte=timezone.now()).order_by('fecha')
    context = {'eventos': eventos_publicos}
    return render(request, 'tickets/lista_eventos.html', context)


def detalle_evento_view(request, evento_id):
    """
    Muestra los detalles de un evento específico que esté aprobado.
    """
    evento = get_object_or_404(Evento, pk=evento_id, aprobado=True)
    context = {'evento': evento}
    return render(request, 'tickets/detalle_evento.html', context)


# ======================================================
# === Vistas del Flujo de Carrito y Compra
# ======================================================

# tickets/views.py

@login_required
def agregar_al_carrito_view(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    carrito = request.session.get('carrito', {})

    if request.method == 'POST':
        hay_boletos_agregados = False
        for boleto in evento.boletos.all():
            # === LÍNEA CORREGIDA ===
            # Si el valor es vacío o None, lo tratamos como "0" por defecto.
            cantidad_str = request.POST.get(f'boleto_{boleto.id}') or "0"
            cantidad = int(cantidad_str)

            if cantidad > 0:
                hay_boletos_agregados = True
                evento_id_str, boleto_id_str = str(evento.id), str(boleto.id)
                if evento_id_str not in carrito:
                    carrito[evento_id_str] = {}
                carrito[evento_id_str][boleto_id_str] = cantidad
        
        if hay_boletos_agregados:
            messages.success(request, f"¡Boletos para '{evento.nombre}' añadidos al carrito!")
        else:
            messages.warning(request, "No seleccionaste ningún boleto.")
            
        request.session['carrito'] = carrito

    return redirect('tickets:detalle_evento', evento_id=evento.id)


@login_required
def ver_carrito_view(request):
    """
    Muestra el contenido detallado del carrito de compras.
    """
    carrito = request.session.get('carrito', {})
    items_del_carrito = []
    total_carrito = 0

    for evento_id, boletos in carrito.items():
        evento = Evento.objects.get(id=int(evento_id))
        for boleto_id, cantidad in boletos.items():
            boleto = Boleto.objects.get(id=int(boleto_id))
            subtotal = boleto.precio * cantidad
            items_del_carrito.append({'evento': evento, 'boleto': boleto, 'cantidad': cantidad, 'subtotal': subtotal})
            total_carrito += subtotal

    context = {'items_del_carrito': items_del_carrito, 'total_carrito': total_carrito}
    return render(request, 'tickets/carrito.html', context)


def actualizar_carrito_view(request):
    """
    Actualiza la cantidad de un item en el carrito via AJAX.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            boleto_id_str = str(data.get('boleto_id'))
            cantidad = int(data.get('cantidad'))
            carrito = request.session.get('carrito', {})

            for evento_id, boletos in carrito.items():
                if boleto_id_str in boletos:
                    boleto_obj = Boleto.objects.get(id=boleto_id_str)
                    stock_disponible = boleto_obj.cantidad_restante
                    if cantidad > stock_disponible:
                        return JsonResponse({'status': 'error', 'message': f'Stock insuficiente. Solo quedan {stock_disponible} boletos.'}, status=400)
                    if cantidad > 0:
                        boletos[boleto_id_str] = cantidad
                    else:
                        del boletos[boleto_id_str]
                    break
            
            carrito_actualizado = {eid: b for eid, b in carrito.items() if b}
            request.session['carrito'] = carrito_actualizado
            
            total_carrito, nuevo_subtotal = 0, 0
            for evento_id, boletos in carrito_actualizado.items():
                for b_id, cant in boletos.items():
                    boleto = Boleto.objects.get(id=int(b_id))
                    total_carrito += boleto.precio * cant
                    if b_id == boleto_id_str:
                        nuevo_subtotal = boleto.precio * cant

            return JsonResponse({'status': 'success', 'nuevo_subtotal': f"${nuevo_subtotal:,.2f}", 'total_carrito': f"${total_carrito:,.2f}"})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


def eliminar_del_carrito_view(request, boleto_id):
    """
    Elimina un item del carrito de compras.
    """
    carrito = request.session.get('carrito', {})
    boleto_id_str = str(boleto_id)
    evento_a_eliminar = None
    for evento_id, boletos in carrito.items():
        if boleto_id_str in boletos:
            evento_a_eliminar = evento_id
            break
    if evento_a_eliminar:
        del carrito[evento_a_eliminar][boleto_id_str]
        if not carrito[evento_a_eliminar]:
            del carrito[evento_a_eliminar]
        messages.success(request, 'Boleto eliminado del carrito.')
    request.session['carrito'] = carrito
    return redirect('tickets:ver_carrito')



@login_required
def checkout_procesar_view(request):
    """
    Procesa el checkout, crea la Venta, envía los correos,
    y luego redirige a la página de éxito.
    """
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('tickets:ver_carrito')

    try:
        with transaction.atomic():
            # ... (la lógica para crear la venta y los detalles se queda igual) ...
            metodo_pago, _ = MetodoPago.objects.get_or_create(nombre='Tarjeta de Crédito (Simulado)')
            venta = Venta.objects.create(usuario=request.user, metodo_pago=metodo_pago, estado='completa')
            
            total_venta_calculado = 0
            for evento_id, boletos in carrito.items():
                for boleto_id, cantidad in boletos.items():
                    boleto = Boleto.objects.get(id=int(boleto_id))
                    if boleto.cantidad_restante < cantidad:
                        raise Exception(f"No hay suficientes boletos para '{boleto.display_name}'.")
                    DetalleVenta.objects.create(venta=venta, boleto=boleto, cantidad=cantidad, precio_unitario=boleto.precio)
                    boleto.cantidad_vendida += cantidad
                    boleto.save()
                    total_venta_calculado += boleto.precio * cantidad

            venta.total_venta = total_venta_calculado
            venta.save()

            # --- LÓGICA DE ENVÍO DE CORREOS MEJORADA ---
            
            # --- CORREO 1: Confirmación de Compra (sin cambios) ---
            subject_confirmacion = f'Confirmación de tu compra en Ticket World - Orden #{venta.id}'
            html_content_confirmacion = render_to_string('tickets/compra_confirmacion_email.html', {'venta': venta})
            email_confirmacion = EmailMultiAlternatives(subject_confirmacion, "", settings.DEFAULT_FROM_EMAIL, [venta.usuario.email])
            email_confirmacion.attach_alternative(html_content_confirmacion, "text/html")
            email_confirmacion.send()

            # --- CORREO 2: Envío de Boletos (con la nueva lógica) ---
            
            # 1. Preparamos una lista de boletos individuales
            boletos_individuales = []
            for detalle in venta.detalles.all():
                for i in range(detalle.cantidad):
                    boletos_individuales.append({
                        'detalle': detalle,
                        'numero': i + 1
                    })

            # 2. Creamos el contexto para el email
            email_context = {
                'venta': venta,
                'boletos_individuales': boletos_individuales
            }
            
            # 3. Renderizamos y enviamos el correo
            subject_boletos = f'Tus boletos para "{venta.detalles.first().boleto.evento.nombre}"'
            html_content_boletos = render_to_string('tickets/boleto_email.html', email_context)
            email_boletos = EmailMultiAlternatives(subject_boletos, "", settings.DEFAULT_FROM_EMAIL, [venta.usuario.email])
            email_boletos.attach_alternative(html_content_boletos, "text/html")
            email_boletos.send()
            
            # ----------------------------------------

            del request.session['carrito']
            request.session.modified = True

    except Exception as e:
        messages.error(request, f"Ocurrió un error al procesar tu compra: {e}")
        return redirect('tickets:ver_carrito')

    return redirect('tickets:compra_exitosa')

@login_required
def compra_exitosa_view(request):
    """
    Muestra la página de confirmación de compra.
    """
    return render(request, 'tickets/compra_exitosa.html')


# ======================================================
# === Vistas para Proveedores
# ======================================================

@login_required
def crear_evento(request):
    if request.user.rol not in ['proveedor', 'admin']:
        messages.error(request, "Solo los proveedores o administradores pueden crear eventos.")
        return redirect('usuarios:inicio')
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        formset = BoletoFormSetCreate(request.POST, request.FILES, prefix='boletos')
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    evento = form.save(commit=False)
                    evento.creado_por = request.user
                    evento.save()
                    formset.instance = evento
                    formset.save()
                    # Lógica de descuento CONADIS
                    boleto_general = Boleto.objects.filter(evento=evento, tipo='general').first()
                    if boleto_general:
                        boleto_conadis = Boleto.objects.filter(evento=evento, tipo='conadis').first()
                        if boleto_conadis:
                            descuento = Decimal(settings.CONADIS_DISCOUNT_PERCENTAGE / 100)
                            precio_descontado = boleto_general.precio * (1 - descuento)
                            boleto_conadis.precio = round(precio_descontado, 2)
                            boleto_conadis.save()
                messages.success(request, f'¡Evento "{evento.nombre}" creado con éxito! Está pendiente de aprobación.')
                return redirect('tickets:mis_eventos')
            except Exception as e:
                messages.error(request, f'Hubo un error al crear el evento: {e}')
    else:
        form = EventoForm()
        formset = BoletoFormSetCreate(prefix='boletos')
    context = { 'form': form, 'formset': formset, 'panel_title': 'Crear Nuevo Evento', 'panel_subtitle': 'Completa los detalles de tu evento y añade al menos un tipo de boleto.', 'button_text': 'Crear Evento' }
    return render(request, 'tickets/crear_evento.html', context)

@login_required
def editar_evento_view(request, evento_id):
    """
    Permite a un proveedor editar un evento existente.
    Versión con la lógica de actualización de stock corregida.
    """
    evento = get_object_or_404(Evento, id=evento_id)

    if evento.creado_por != request.user and not request.user.is_superuser:
        messages.error(request, "No tienes permiso para editar este evento.")
        return redirect('tickets:mis_eventos')

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        formset = BoletoFormSetEdit(request.POST, request.FILES, instance=evento, prefix='boletos')

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    formset.save()

                    # === LÓGICA DE STOCK CORREGIDA Y SIMPLIFICADA ===
                    for boleto_form in formset:
                        # Solo procesamos boletos que ya existen (tienen un .pk)
                        if boleto_form.instance.pk:
                            # Obtenemos el valor directamente del formulario validado
                            cantidad_a_modificar = boleto_form.cleaned_data.get('anadir_quitar_stock')
                            
                            # Si el proveedor introdujo un número en el campo "Añadir/Quitar"...
                            if cantidad_a_modificar: # (Esto es suficiente, no necesitamos has_changed())
                                boleto = boleto_form.instance
                                boleto.cantidad_total += cantidad_a_modificar
                                boleto.save(update_fields=['cantidad_total'])

                    # La lógica del descuento CONADIS se ejecuta después para asegurar consistencia
                    boleto_general = Boleto.objects.filter(evento=evento, tipo='general').first()
                    if boleto_general:
                        boleto_conadis = Boleto.objects.filter(evento=evento, tipo='conadis').first()
                        if boleto_conadis:
                            descuento = Decimal(settings.CONADIS_DISCOUNT_PERCENTAGE / 100)
                            precio_descontado = boleto_general.precio * (1 - descuento)
                            boleto_conadis.precio = round(precio_descontado, 2)
                            boleto_conadis.save()
                
                messages.success(request, f'El evento "{evento.nombre}" ha sido actualizado con éxito.')
                return redirect('tickets:mis_eventos')

            except Exception as e:
                messages.error(request, f'Hubo un error al guardar los cambios: {e}')
        else:
            messages.error(request, 'Por favor, corrige los errores mostrados en el formulario.')

    else: # GET
        form = EventoForm(instance=evento)
        formset = BoletoFormSetEdit(instance=evento, prefix='boletos')

    context = {
        'form': form,
        'formset': formset,
        'panel_title': 'Editar Evento',
        'panel_subtitle': f'Estás editando los detalles de "{evento.nombre}".',
        'button_text': 'Guardar Cambios'
    }
    return render(request, 'tickets/crear_evento.html', context)
@login_required
def mis_eventos_view(request):
    if request.user.rol not in ['proveedor', 'admin']:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('usuarios:inicio')
    eventos_del_proveedor = Evento.objects.filter(creado_por=request.user).order_by('-creado_en')
    context = {'eventos': eventos_del_proveedor}
    return render(request, 'tickets/mis_eventos.html', context)


# ======================================================
# === Vistas de Administración
# ======================================================

@admin_required
def gestion_eventos(request):
    """
    Muestra una página de gestión de todos los eventos para el admin.
    """
    eventos = Evento.objects.all().order_by('-fecha')
    context = {'eventos': eventos}
    return render(request, 'tickets/gestion_eventos.html', context)


@admin_required
def lista_eventos_pendientes(request):
    eventos_pendientes = Evento.objects.filter(aprobado=False).order_by('-creado_en')
    context = {
        'eventos': eventos_pendientes,
        'panel_title': 'Eventos Pendientes de Aprobación',
        'panel_subtitle': 'Revisa los eventos creados por los proveedores y decide cuáles se publicarán.'
    }
    return render(request, 'tickets/lista_eventos.html', context)


@admin_required
def aprobar_evento(request, evento_id):
    if request.method == 'POST':
        evento = get_object_or_404(Evento, pk=evento_id)
        evento.aprobado = True
        evento.save()
        messages.success(request, f'El evento "{evento.nombre}" ha sido aprobado y ahora es visible públicamente.')
    return redirect('tickets:lista_eventos_pendientes')


@admin_required
def rechazar_evento(request, evento_id):
    if request.method == 'POST':
        evento = get_object_or_404(Evento, pk=evento_id)
        evento_nombre = evento.nombre
        evento.delete()
        messages.warning(request, f'El evento "{evento_nombre}" ha sido rechazado y eliminado del sistema.')
    return redirect('tickets:lista_eventos_pendientes')