# tickets/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from usuarios.decorators import admin_required # Asumo que admin_required está en esta ruta
from django.db import transaction # <-- ¡Importa transaction para asegurar la atomicidad!

from .models import Evento, Categoria, Boleto, Venta, DetalleVenta, MetodoPago # Modelos optimizados
from .forms import EventoForm, BoletoFormSet # <-- ¡Importa el Formset!
from django.conf import settings # <-- AÑADE ESTE IMPORT AL PRINCIPIO
from decimal import Decimal      # <-- Y ESTE TAMBIÉN
import json # <-- AÑADE ESTE IMPORT AL PRINCIPIO
from django.http import JsonResponse # <-- Y ESTE TAMBIÉN

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


@login_required
def crear_evento(request):
    if request.user.rol not in ['proveedor', 'admin']:
        messages.error(request, "Solo los proveedores o administradores pueden crear eventos.")
        return redirect('usuarios:inicio')

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        formset = BoletoFormSet(request.POST, request.FILES, prefix='boletos')

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    evento = form.save(commit=False)
                    evento.creado_por = request.user
                    evento.aprobado = False
                    evento.esta_activo = True
                    evento.save()

                    # Guardamos los boletos tal como vienen del formulario
                    boletos = formset.save(commit=False)
                    boleto_general = None
                    boleto_conadis = None

                    for boleto in boletos:
                        boleto.evento = evento
                        boleto.save()
                        # Identificamos el boleto general y el de CONADIS para usarlos después
                        if boleto.tipo == 'general':
                            boleto_general = boleto
                        if boleto.tipo == 'conadis':
                            boleto_conadis = boleto
                    
                    # === LÓGICA DEL DESCUENTO AUTOMÁTICO ===
                    if boleto_conadis and boleto_general:
                        # Si existen ambos boletos, calculamos y aplicamos el descuento.
                        descuento = Decimal(settings.CONADIS_DISCOUNT_PERCENTAGE / 100)
                        precio_descontado = boleto_general.precio * (1 - descuento)
                        
                        # Actualizamos el precio del boleto CONADIS y lo guardamos
                        boleto_conadis.precio = precio_descontado.quantize(Decimal('0.01'))
                        boleto_conadis.save()
                        
                        messages.info(request, f"Se aplicó un descuento del {settings.CONADIS_DISCOUNT_PERCENTAGE}% al boleto CONADIS.")

                    formset.save_m2m()
                    messages.success(request, f'¡Evento "{evento.nombre}" creado con éxito! Está pendiente de aprobación.')
                    return redirect('usuarios:inicio') # Redirigir a "Mis Eventos" sería ideal a futuro

            except Exception as e:
                messages.error(request, f'Hubo un error al crear el evento: {e}')
    else:
        form = EventoForm()
        formset = BoletoFormSet(prefix='boletos')

    context = {
        'form': form,
        'formset': formset,
        'panel_title': 'Crear Nuevo Evento',
        'panel_subtitle': 'Completa los detalles de tu evento y añade al menos un tipo de boleto.',
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

def detalle_evento_view(request, evento_id):
    """
    Muestra los detalles de un evento específico que esté aprobado.
    """
    # get_object_or_404 busca el evento por su ID y que esté aprobado.
    # Si no lo encuentra, automáticamente muestra una página de "Error 404: No Encontrado".
    evento = get_object_or_404(Evento, pk=evento_id, aprobado=True)
    
    # Pasamos el objeto 'evento' encontrado a la plantilla.
    context = {
        'evento': evento
    }
    
    return render(request, 'tickets/detalle_evento.html', context)
     
@login_required
def agregar_al_carrito_view(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    
    # Inicializamos el carrito en la sesión si no existe
    # El carrito será un diccionario. Ej: {'1': {'2': 3}} -> Evento 1, Boleto 2, 3 unidades
    carrito = request.session.get('carrito', {})

    if request.method == 'POST':
        hay_boletos_agregados = False
        # Recorremos los boletos del evento para ver cuántos seleccionó el usuario
        for boleto in evento.boletos.all():
            cantidad_str = request.POST.get(f'boleto_{boleto.id}', '0')
            cantidad = int(cantidad_str)

            if cantidad > 0:
                # Si el usuario seleccionó al menos un boleto de este tipo
                hay_boletos_agregados = True
                
                # Convertimos los IDs a string porque JSON (usado por las sesiones) no usa claves enteras
                evento_id_str = str(evento.id)
                boleto_id_str = str(boleto.id)

                # Creamos la entrada para el evento si no existe
                if evento_id_str not in carrito:
                    carrito[evento_id_str] = {}
                
                # Añadimos o actualizamos la cantidad de boletos
                carrito[evento_id_str][boleto_id_str] = cantidad
        
        if hay_boletos_agregados:
            messages.success(request, f"¡Boletos para '{evento.nombre}' añadidos al carrito!")
        else:
            messages.warning(request, "No seleccionaste ningún boleto.")
            
        # Guardamos el carrito actualizado en la sesión
        request.session['carrito'] = carrito

        # Imprimimos el carrito en la terminal para depurar (opcional)
        print("Carrito actualizado:", request.session.get('carrito'))

    # Redirigimos de vuelta a la página de detalles del evento
    return redirect('tickets:detalle_evento', evento_id=evento.id)

@login_required
def ver_carrito_view(request):
    # Obtenemos el carrito de la sesión
    carrito = request.session.get('carrito', {})
    
    items_del_carrito = []
    total_carrito = 0

    # Procesamos el carrito para obtener los objetos y calcular totales
    for evento_id, boletos in carrito.items():
        evento = Evento.objects.get(id=int(evento_id))
        for boleto_id, cantidad in boletos.items():
            boleto = Boleto.objects.get(id=int(boleto_id))
            subtotal = boleto.precio * cantidad
            
            # Añadimos un diccionario con toda la información a nuestra lista
            items_del_carrito.append({
                'evento': evento,
                'boleto': boleto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total_carrito += subtotal

    context = {
        'items_del_carrito': items_del_carrito,
        'total_carrito': total_carrito,
    }
    
    return render(request, 'tickets/carrito.html', context)

@login_required # Solo usuarios logueados pueden finalizar una compra
def checkout_procesar_view(request):
    """
    Procesa el carrito, crea la Venta y los Detalles de Venta,
    y luego redirige a la página de éxito.
    """
    carrito = request.session.get('carrito', {})
    if not carrito:
        # Si el carrito está vacío, no hay nada que procesar.
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('tickets:ver_carrito')

    # Usamos una transacción atómica. Si algo falla durante el proceso,
    # todos los cambios en la base de datos se revierten. Es un todo o nada.
    try:
        with transaction.atomic():
            # 1. Crear el objeto Venta
            
            # Como aún no tenemos un formulario de pago, obtendremos o crearemos un método por defecto.
            metodo_pago, _ = MetodoPago.objects.get_or_create(nombre='Tarjeta de Crédito (Simulado)')
            
            venta = Venta.objects.create(
                usuario=request.user,
                metodo_pago=metodo_pago
                # El total se calculará y guardará después
            )
            
            total_venta_calculado = 0

            # 2. Recorrer el carrito para crear los Detalles de Venta
            for evento_id, boletos in carrito.items():
                for boleto_id, cantidad in boletos.items():
                    boleto = Boleto.objects.get(id=int(boleto_id))
                    
                    # Comprobación de stock (opcional pero recomendado)
                    if (boleto.cantidad_total - boleto.cantidad_vendida) < cantidad:
                        # Si no hay suficientes boletos, lanzamos un error y la transacción se revertirá.
                        raise Exception(f"No hay suficientes boletos para '{boleto.nombre_boleto}'.")

                    DetalleVenta.objects.create(
                        venta=venta,
                        boleto=boleto,
                        cantidad=cantidad,
                        precio_unitario=boleto.precio
                    )
                    
                    # Actualizamos la cantidad de boletos vendidos
                    boleto.cantidad_vendida += cantidad
                    boleto.save()
                    
                    total_venta_calculado += boleto.precio * cantidad

            # 3. Actualizamos el total en la Venta principal
            venta.total_venta = total_venta_calculado
            venta.save()

            # 4. Limpiamos el carrito de la sesión
            del request.session['carrito']
            request.session.modified = True

    except Exception as e:
        # Si algo falló (ej. falta de stock), mostramos un error.
        messages.error(request, f"Ocurrió un error al procesar tu compra: {e}")
        return redirect('tickets:ver_carrito')

    # 5. Todo salió bien, redirigimos a la página de éxito.
    return redirect('tickets:compra_exitosa')


@login_required
def compra_exitosa_view(request):
    """
    Muestra una página de confirmación después de una compra exitosa.
    """
    # Esta vista solo necesita renderizar la plantilla.
    return render(request, 'tickets/compra_exitosa.html')

def eliminar_del_carrito_view(request, boleto_id):
    carrito = request.session.get('carrito', {})
    boleto_id_str = str(boleto_id) # Las claves en el carrito son strings

    # Buscamos en qué evento está el boleto para poder eliminarlo
    evento_a_eliminar = None
    for evento_id, boletos in carrito.items():
        if boleto_id_str in boletos:
            evento_a_eliminar = evento_id
            break

    if evento_a_eliminar:
        # Eliminamos el boleto del diccionario de ese evento
        del carrito[evento_a_eliminar][boleto_id_str]
        
        # Si ya no quedan más tipos de boletos de ese evento, eliminamos el evento entero del carrito
        if not carrito[evento_a_eliminar]:
            del carrito[evento_a_eliminar]
        
        messages.success(request, 'Boleto eliminado del carrito.')
    
    # Guardamos los cambios en la sesión
    request.session['carrito'] = carrito
    
    # Redirigimos de vuelta a la página del carrito
    return redirect('tickets:ver_carrito')

def actualizar_carrito_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            boleto_id_str = str(data.get('boleto_id'))
            cantidad = int(data.get('cantidad'))
            
            carrito = request.session.get('carrito', {})

            # Lógica para actualizar o eliminar el boleto del carrito
            for evento_id, boletos in carrito.items():
                if boleto_id_str in boletos:
                    if cantidad > 0:
                        boleto_obj = Boleto.objects.get(id=boleto_id_str)
                        stock_disponible = boleto_obj.cantidad_total - boleto_obj.cantidad_vendida
                        if cantidad > stock_disponible:
                             return JsonResponse({'status': 'error', 'message': 'Stock insuficiente'}, status=400)
                        boletos[boleto_id_str] = cantidad
                    else:
                        del boletos[boleto_id_str]
                    break
            
            carrito_actualizado = {eid: b for eid, b in carrito.items() if b}
            request.session['carrito'] = carrito_actualizado
            
            # === LÓGICA AÑADIDA: Recalcular totales y devolverlos ===
            total_carrito = 0
            nuevo_subtotal = 0
            for evento_id, boletos in carrito_actualizado.items():
                for b_id, cant in boletos.items():
                    boleto = Boleto.objects.get(id=int(b_id))
                    total_carrito += boleto.precio * cant
                    if b_id == boleto_id_str:
                        nuevo_subtotal = boleto.precio * cant

            return JsonResponse({
                'status': 'success',
                'nuevo_subtotal': f"${nuevo_subtotal:,.2f}",
                'total_carrito': f"${total_carrito:,.2f}",
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@login_required
def mis_eventos_view(request):
    """
    Muestra al proveedor una lista de los eventos que ha creado.
    """
    # Verificamos que el usuario tenga el rol correcto para ver esta página
    if request.user.rol not in ['proveedor', 'admin']:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('usuarios:inicio')

    # Buscamos todos los eventos donde 'creado_por' es el usuario actual
    # y los ordenamos por el más reciente primero.
    eventos_del_proveedor = Evento.objects.filter(creado_por=request.user).order_by('-creado_en')
    
    context = {
        'eventos': eventos_del_proveedor
    }
    
    return render(request, 'tickets/mis_eventos.html', context)