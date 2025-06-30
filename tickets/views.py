import json
import threading
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.db.models import Avg, Count, Sum, F
from django.urls import reverse
from django.db.models.functions import TruncDate, TruncMonth
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime
from collections import defaultdict
from io import BytesIO
import qrcode
from email.mime.image import MIMEImage
import uuid
import time

# --- Imports de nuestras aplicaciones ---
from usuarios.decorators import admin_required
from .models import Evento, Categoria, Boleto, Venta, DetalleVenta, MetodoPago, Opinion
from usuarios.models import UserNotification, SolicitudProveedor
# ¡ASEGÚRATE DE QUE ESTA FUNCIÓN ESTÉ DISPONIBLE O QUÍTALA SI NO EXISTE!
# Si no existe, puedes definir una función vacía: def create_web_notification(*args, **kwargs): pass
from usuarios.views import create_web_notification 

# --- CAMBIO IMPORTANTE: AHORA IMPORTAMOS DESDE FORMS.PY ---
from .forms import EventoForm, BoletoFormSetCreate, BoletoFormSetEdit, OpinionForm


# ======================================================
# === CONSTANTE DE COMISIÓN
# ======================================================
TASA_COMISION = Decimal('0.05')

# ... (El resto del archivo es idéntico al que te pasé antes, lo incluyo para que sea copiar y pegar)
# ======================================================
# === FUNCIONES AYUDANTES
# ======================================================

def _attach_event_stats(eventos_list):
    if not eventos_list:
        return []
    ids_eventos = [evento.id for evento in eventos_list]
    datos_agregados = DetalleVenta.objects.filter(
        boleto__evento_id__in=ids_eventos,
        venta__estado='completa'
    ).values(
        'boleto__evento_id'
    ).annotate(
        total_tickets=Sum('cantidad'),
        total_revenue=Sum(F('cantidad') * F('precio_unitario'))
    )
    mapa_datos = {
        item['boleto__evento_id']: {
            'tickets': item.get('total_tickets', 0),
            'revenue': item.get('total_revenue', Decimal('0.00'))
        }
        for item in datos_agregados
    }
    for evento in eventos_list:
        datos = mapa_datos.get(evento.id)
        if datos:
            evento.total_boletos_vendidos_annotated = datos['tickets']
            evento.ingresos_generados_annotated = datos['revenue']
        else:
            evento.total_boletos_vendidos_annotated = 0
            evento.ingresos_generados_annotated = Decimal('0.00')
    return eventos_list


def enviar_correo_completo_en_hilo(subject, html_content, recipient_list, attachments=None):
    try:
        email = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, recipient_list)
        email.attach_alternative(html_content, "text/html")
        if attachments:
            for attachment in attachments:
                email.attach(attachment)
        email.send()
        print(f"Correo '{subject}' encolado para envío en segundo plano.")
    except Exception as e:
        print(f"ERROR en el hilo de envío de correo: {e}")


def _get_common_event_context(request):
    favorited_event_ids = set()
    if request.user.is_authenticated:
        favorited_event_ids = set(request.user.eventos_favoritos.values_list('id', flat=True))
    return favorited_event_ids


# ======================================================
# === Vistas Públicas Generales
# ======================================================

def index(request):
    return HttpResponse("¡Bienvenido a la sección de tickets!")

def lista_eventos(request):
    eventos_list = Evento.objects.filter(aprobado=True, fecha__gte=timezone.now()) \
        .select_related('categoria', 'creado_por').order_by('fecha')
    paginator = Paginator(eventos_list, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'eventos': page_obj, 'page_obj': page_obj, 'panel_title': 'Próximos Eventos',
        'panel_subtitle': 'Descubre los eventos que están por venir.', 'favorited_event_ids': _get_common_event_context(request),
    }
    return render(request, 'tickets/lista_eventos.html', context)

def detalle_evento_view(request, evento_id):
    # Optimización: prefetch de boletos y select_related de categoría
    evento = get_object_or_404(
        Evento.objects.select_related('categoria').prefetch_related('boletos'),
        pk=evento_id, aprobado=True
    )
    # Optimización: select_related de usuario en opiniones
    opiniones = Opinion.objects.filter(evento=evento, estado='aprobada').select_related('usuario').order_by('-fecha_opinion')
    estadisticas_opinion = opiniones.aggregate(avg_calificacion=Avg('calificacion'), num_opiniones=Count('id'))
    opinion_form, puede_dejar_opinion, usuario_ya_opino, ha_comprado = None, False, False, False
    evento_pasado = evento.fecha < timezone.now()

    if request.user.is_authenticated:
        if evento_pasado:
            ha_comprado = Venta.objects.filter(usuario=request.user, detalles__boleto__evento=evento, estado='completa').exists()
            if ha_comprado:
                usuario_ya_opino = Opinion.objects.filter(evento=evento, usuario=request.user).exists()
                if not usuario_ya_opino:
                    puede_dejar_opinion = True
                    if request.method == 'POST' and 'submit_opinion' in request.POST:
                        opinion_form = OpinionForm(request.POST)
                        if opinion_form.is_valid():
                            opinion = opinion_form.save(commit=False)
                            opinion.evento, opinion.usuario, opinion.estado = evento, request.user, 'pendiente'
                            opinion.save()
                            messages.success(request, "¡Gracias por tu opinión! Será visible una vez aprobada.")
                            return redirect('tickets:detalle_evento', evento_id=evento.id)
                        else:
                            messages.error(request, "Hubo un error con tu opinión.")
                    else:
                        opinion_form = OpinionForm()
    
    is_favorited = False
    if request.user.is_authenticated:
        # Optimización: obtener IDs de favoritos una sola vez
        fav_ids = set(request.user.eventos_favoritos.values_list('id', flat=True))
        is_favorited = evento.id in fav_ids

    latitud_formateada = f"{round(evento.latitud, 6)}" if evento.latitud is not None else ""
    longitud_formateada = f"{round(evento.longitud, 6)}" if evento.longitud is not None else ""

    context = {
        'evento': evento, 
        'opiniones': opiniones, 
        'avg_calificacion': estadisticas_opinion['avg_calificacion'],
        'num_opiniones': estadisticas_opinion['num_opiniones'], 
        'opinion_form': opinion_form,
        'puede_dejar_opinion': puede_dejar_opinion, 
        'usuario_ya_opino': usuario_ya_opino,
        'evento_pasado': evento_pasado, 
        'ha_comprado': ha_comprado, 
        'is_favorited': is_favorited,
        'favorited_event_ids': _get_common_event_context(request),
        'latitud_formateada': latitud_formateada,
        'longitud_formateada': longitud_formateada,
    }
    return render(request, 'tickets/detalle_evento.html', context)


@login_required
def lista_eventos_pasados(request):
    eventos_list = Evento.objects.filter(aprobado=True, fecha__lt=timezone.now()).order_by('-fecha')
    paginator = Paginator(eventos_list, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'eventos': page_obj, 'page_obj': page_obj, 'panel_title': 'Eventos Pasados',
        'panel_subtitle': 'Explora eventos que ya han terminado y deja tu opinión.', 'favorited_event_ids': _get_common_event_context(request),
    }
    return render(request, 'tickets/lista_eventos.html', context)

# ======================================================
# === Vistas del Flujo de Carrito y Compra
# ======================================================

@login_required
def agregar_al_carrito_view(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    carrito = request.session.get('carrito', {})
    if request.method == 'POST':
        hay_boletos_agregados = False
        for boleto in evento.boletos.all():
            cantidad = int(request.POST.get(f'boleto_{boleto.id}', "0"))
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
    start_time = time.time()
    carrito = request.session.get('carrito', {})
    t1 = time.time()
    evento_ids = [int(eid) for eid in carrito.keys()]
    boleto_ids = [int(bid) for boletos in carrito.values() for bid in boletos.keys()]
    eventos = Evento.objects.in_bulk(evento_ids)
    boletos = Boleto.objects.in_bulk(boleto_ids)
    t2 = time.time()
    items_del_carrito, total_carrito = [], 0
    for evento_id, boletos_dict in carrito.items():
        evento = eventos.get(int(evento_id))
        for boleto_id, cantidad in boletos_dict.items():
            boleto = boletos.get(int(boleto_id))
            if evento and boleto:
                subtotal = boleto.precio * cantidad
                items_del_carrito.append({'evento': evento, 'boleto': boleto, 'cantidad': cantidad, 'subtotal': subtotal})
                total_carrito += subtotal
    t3 = time.time()
    context = {'items_del_carrito': items_del_carrito, 'total_carrito': total_carrito}
    response = render(request, 'tickets/carrito.html', context)
    t4 = time.time()
    print(f"[DEBUG] Tiempo total ver_carrito_view: {(t4-start_time)*1000:.2f} ms")
    print(f"[DEBUG] Tiempo consultas DB: {(t2-t1)*1000:.2f} ms")
    print(f"[DEBUG] Tiempo construcción items_del_carrito: {(t3-t2)*1000:.2f} ms")
    print(f"[DEBUG] Tiempo renderizado template: {(t4-t3)*1000:.2f} ms")
    return response

def actualizar_carrito_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            boleto_id_str, cantidad = str(data.get('boleto_id')), int(data.get('cantidad'))
            carrito = request.session.get('carrito', {})
            for evento_id, boletos in carrito.items():
                if boleto_id_str in boletos:
                    boleto_obj = Boleto.objects.get(id=boleto_id_str)
                    if cantidad > boleto_obj.cantidad_restante:
                        return JsonResponse({'status': 'error', 'message': f'Stock insuficiente. Solo quedan {boleto_obj.cantidad_restante} boletos.'}, status=400)
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
    carrito = request.session.get('carrito', {})
    boleto_id_str = str(boleto_id)
    for evento_id, boletos in list(carrito.items()):
        if boleto_id_str in boletos:
            del boletos[boleto_id_str]
            if not boletos:
                del carrito[evento_id]
            messages.success(request, 'Boleto eliminado del carrito.')
            break
    request.session['carrito'] = carrito
    return redirect('tickets:ver_carrito')

@login_required
def checkout_procesar_view(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('tickets:ver_carrito')
    try:
        venta_id = None
        with transaction.atomic():
            ids_boletos_en_carrito = [int(id_str) for boletos in carrito.values() for id_str in boletos.keys()]
            boletos_qs = Boleto.objects.select_related('evento').filter(id__in=ids_boletos_en_carrito)
            boletos_dict = {boleto.id: boleto for boleto in boletos_qs}
            for boleto_id, cantidad_deseada in [(int(bid), c) for boletos in carrito.values() for bid, c in boletos.items()]:
                boleto = boletos_dict.get(boleto_id)
                if not boleto or boleto.cantidad_restante < cantidad_deseada:
                    messages.error(request, f"Stock insuficiente para '{boleto.display_name if boleto else 'un boleto'}.")
                    return redirect('tickets:ver_carrito')
            
            metodo_pago, _ = MetodoPago.objects.get_or_create(nombre='Tarjeta de Crédito (Simulado)')
            venta = Venta.objects.create(usuario=request.user, metodo_pago=metodo_pago, estado='completa')
            
            detalles_a_crear, boletos_a_actualizar = [], []
            total_bruto_calculado = Decimal('0.00')

            for evento_id, boletos in carrito.items():
                for boleto_id_str, cantidad in boletos.items():
                    boleto = boletos_dict[int(boleto_id_str)]
                    detalles_a_crear.append(DetalleVenta(venta=venta, boleto=boleto, cantidad=cantidad, precio_unitario=boleto.precio))
                    boleto.cantidad_vendida += cantidad
                    boletos_a_actualizar.append(boleto)
                    total_bruto_calculado += boleto.precio * cantidad
            
            DetalleVenta.objects.bulk_create(detalles_a_crear)
            Boleto.objects.bulk_update(boletos_a_actualizar, ['cantidad_vendida'])
            
            comision_calculada = total_bruto_calculado * TASA_COMISION
            ganancia_proveedor_calculada = total_bruto_calculado - comision_calculada

            venta.total_bruto = total_bruto_calculado
            venta.comision_plataforma = comision_calculada
            venta.ganancia_proveedor = ganancia_proveedor_calculada
            venta.save()
            
            venta_id = venta.id
            primer_evento_nombre = boletos_a_actualizar[0].evento.nombre if boletos_a_actualizar else "Varios Eventos"
            create_web_notification(request.user, 'compra', f'¡Tu compra para "{primer_evento_nombre}" ha sido exitosa!', link=reverse('usuarios:perfil') + '#mis-entradas')
            del request.session['carrito']
            request.session.modified = True
        
        if venta_id:
            try:
                venta_completa = Venta.objects.prefetch_related('detalles__boleto__evento__categoria', 'usuario').get(id=venta_id)
                recipient = [venta_completa.usuario.email]
                subject_confirmacion = f'Confirmación de tu compra en Ticket World - Orden #{venta_completa.id}'
                html_content_confirmacion = render_to_string('tickets/compra_confirmacion_email.html', {'venta': venta_completa})
                threading.Thread(target=enviar_correo_completo_en_hilo, args=(subject_confirmacion, html_content_confirmacion, recipient)).start()
                subject_boletos = f'Tus boletos para "{venta_completa.detalles.first().boleto.evento.nombre}"'
                boletos_con_qr, imagenes_adjuntas = [], []
                for detalle in venta_completa.detalles.all():
                    for i in range(detalle.cantidad):
                        identificador_unico = f'{detalle.boleto_uuid}-{i+1}'
                        qr_data = f"https://tu-dominio.com/validar/{identificador_unico}/"
                        qr_img = qrcode.make(qr_data)
                        buffer = BytesIO()
                        qr_img.save(buffer, "PNG")
                        buffer.seek(0)
                        qr_mime_image = MIMEImage(buffer.read())
                        qr_mime_image.add_header('Content-ID', f'<{identificador_unico}>')
                        imagenes_adjuntas.append(qr_mime_image)
                        boletos_con_qr.append({'detalle': detalle, 'cid': identificador_unico, 'numero_asiento': i + 1, 'total_asientos': detalle.cantidad})
                contexto_boletos = {'venta': venta_completa, 'boletos_individuales': boletos_con_qr}
                html_content_boletos = render_to_string('tickets/boleto_email_con_qr.html', contexto_boletos)
                threading.Thread(target=enviar_correo_completo_en_hilo, args=(subject_boletos, html_content_boletos, recipient, imagenes_adjuntas)).start()
            except Exception as e:
                print(f"ERROR: No se pudo preparar/iniciar hilos de correo para venta #{venta_id}: {e}")
    except Exception as e:
        messages.error(request, f"Ocurrió un error crítico al procesar tu compra: {e}")
        return redirect('tickets:ver_carrito')
    return redirect('tickets:compra_exitosa')

@login_required
def compra_exitosa_view(request):
    return render(request, 'tickets/compra_exitosa.html')

# ======================================================
# === Vistas para Proveedores
# ======================================================

@login_required
def crear_evento(request):
    if request.user.rol not in ['proveedor', 'admin']:
        messages.error(request, "Solo los proveedores pueden crear eventos.")
        return redirect('usuarios:inicio')
        
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        formset = BoletoFormSetCreate(request.POST, request.FILES, prefix='boletos')
        
        if form.is_valid() and formset.is_valid():
            
            precio_general = None
            conadis_form = None

            for form_individual, cleaned_data in zip(formset.forms, formset.cleaned_data):
                tipo_boleto = cleaned_data.get('tipo')
                
                if tipo_boleto == 'general':
                    precio_general = cleaned_data.get('precio')
                
                if tipo_boleto == 'conadis':
                    conadis_form = form_individual

            if precio_general is not None and conadis_form is not None:
                precio_conadis_calculado = precio_general * Decimal('0.80')
                conadis_form.instance.precio = precio_conadis_calculado
            
            with transaction.atomic():
                evento = form.save(commit=False)
                evento.creado_por = request.user
                evento.save()
                
                formset.instance = evento
                formset.save()
                
            messages.success(request, f'¡Evento "{evento.nombre}" creado con éxito! Está pendiente de aprobación.')
            return redirect('tickets:panel_proveedor')
    else:
        form = EventoForm()
        formset = BoletoFormSetCreate(prefix='boletos')
        
    context = {'form': form, 'formset': formset, 'panel_title': 'Crear Nuevo Evento', 'button_text': 'Crear Evento'}
    return render(request, 'tickets/crear_evento.html', context)

@login_required
def editar_evento_view(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if evento.creado_por != request.user and not request.user.is_superuser:
        messages.error(request, "No tienes permiso para editar este evento.")
        return redirect('tickets:panel_proveedor')
        
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        formset = BoletoFormSetEdit(request.POST, request.FILES, instance=evento, prefix='boletos')
        
        if form.is_valid() and formset.is_valid():
            
            precio_general = None
            conadis_form = None

            for form_individual, cleaned_data in zip(formset.forms, formset.cleaned_data):
                if cleaned_data.get('DELETE'):
                    continue
                tipo_boleto = cleaned_data.get('tipo')
                if tipo_boleto == 'general':
                    precio_general = cleaned_data.get('precio')
                if tipo_boleto == 'conadis':
                    conadis_form = form_individual

            if precio_general is not None and conadis_form is not None:
                precio_conadis_calculado = precio_general * Decimal('0.80')
                conadis_form.instance.precio = precio_conadis_calculado

            form.save()
            formset.save()
            
            messages.success(request, f'El evento "{evento.nombre}" ha sido actualizado con éxito.')
            return redirect('tickets:panel_proveedor')
    else:
        form = EventoForm(instance=evento)
        formset = BoletoFormSetEdit(instance=evento, prefix='boletos')
        
    context = {'form': form, 'formset': formset, 'panel_title': 'Editar Evento', 'button_text': 'Guardar Cambios'}
    return render(request, 'tickets/crear_evento.html', context)


@login_required
def reporte_ventas_view(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if evento.creado_por != request.user and not request.user.is_superuser:
        messages.error(request, "No tienes permiso para ver el reporte de este evento.")
        return redirect('tickets:panel_proveedor')

    # Optimización: obtener todas las ventas completas del evento y sus detalles en una sola consulta
    ventas_del_evento = Venta.objects.filter(
        detalles__boleto__evento=evento, estado='completa'
    ).distinct().order_by('-fecha_compra') \
     .select_related('usuario', 'metodo_pago') \
     .prefetch_related('detalles__boleto')

    # IDs de ventas para usar en agregaciones
    ventas_ids = ventas_del_evento.values_list('id', flat=True)

    # Agregados globales en una sola consulta
    agregados = Venta.objects.filter(id__in=ventas_ids).aggregate(
        total_ganancia=Sum('ganancia_proveedor'),
        total_bruto=Sum('total_bruto'),
        total_ordenes=Count('id')
    )

    ganancias_netas_totales = agregados['total_ganancia'] or 0
    ingresos_brutos_totales = agregados['total_bruto'] or 0
    ordenes_totales = agregados['total_ordenes'] or 0
    ganancia_promedio_orden = (ganancias_netas_totales / ordenes_totales) if ordenes_totales > 0 else 0

    # Ventas por día (una sola consulta)
    ventas_por_dia = Venta.objects.filter(id__in=ventas_ids).annotate(
        dia=TruncDate('fecha_compra')
    ).values('dia').annotate(
        total_ventas=Sum('ganancia_proveedor')
    ).order_by('dia')
    labels_grafico_lineas = [v['dia'].strftime('%d %b') for v in ventas_por_dia]
    data_grafico_lineas = [float(v['total_ventas']) for v in ventas_por_dia]

    # Boletos por tipo (una sola consulta, sin venta__in costoso)
    boletos_por_tipo = DetalleVenta.objects.filter(
        venta__id__in=ventas_ids
    ).values('boleto__tipo').annotate(
        cantidad_total=Sum('cantidad')
    ).order_by('-cantidad_total')
    labels_grafico_pie = [b['boleto__tipo'].capitalize() for b in boletos_por_tipo]
    data_grafico_pie = [b['cantidad_total'] for b in boletos_por_tipo]

    paginator = Paginator(ventas_del_evento, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'evento': evento, 'page_obj': page_obj, 
        'ganancias_netas_totales': ganancias_netas_totales,
        'ingresos_brutos_totales': ingresos_brutos_totales,
        'boletos_vendidos': ordenes_totales, 
        'ordenes_totales': ordenes_totales,
        'ganancia_promedio_orden': ganancia_promedio_orden,
        'labels_grafico_lineas': json.dumps(labels_grafico_lineas),
        'data_grafico_lineas': json.dumps(data_grafico_lineas),
        'labels_grafico_pie': json.dumps(labels_grafico_pie),
        'data_grafico_pie': json.dumps(data_grafico_pie),
    }
    return render(request, 'tickets/reporte_ventas.html', context)


@login_required
def panel_proveedor_view(request):
    if request.user.rol not in ['proveedor', 'admin']:
        messages.error(request, "Acceso denegado.")
        return redirect('usuarios:inicio')

    eventos_proveedor = Evento.objects.filter(creado_por=request.user)
    eventos_ids = list(eventos_proveedor.values_list('id', flat=True))

    # Un solo query para ambos agregados de ganancias
    from django.db.models import Case, When, DecimalField
    hace_30_dias = timezone.now() - timedelta(days=30)
    agregados = Venta.objects.filter(
        detalles__boleto__evento__in=eventos_ids, estado='completa'
    ).aggregate(
        total_sum=Sum('ganancia_proveedor'),
        total_sum_30=Sum(Case(
            When(fecha_compra__gte=hace_30_dias, then='ganancia_proveedor'),
            default=0,
            output_field=DecimalField()
        ))
    )
    ganancias_totales = agregados['total_sum'] or 0
    ganancias_30_dias = agregados['total_sum_30'] or 0

    eventos_publicados_count = len(eventos_ids)
    ganancia_promedio_evento = (ganancias_totales / eventos_publicados_count) if eventos_publicados_count > 0 else 0

    # Ganancias por mes (todo en DB)
    ventas_globales = Venta.objects.filter(
        detalles__boleto__evento__in=eventos_ids, estado='completa'
    )
    ventas_por_mes = ventas_globales.annotate(
        mes=TruncMonth('fecha_compra')
    ).values('mes').annotate(
        total_mes=Sum('ganancia_proveedor')
    ).order_by('mes')
    labels_ingresos_mes = [v['mes'].strftime('%b %Y') for v in ventas_por_mes]
    data_ingresos_mes = [float(v['total_mes']) for v in ventas_por_mes]

    # Top 5 eventos por ganancia (todo en DB)
    ganancias_por_evento_qs = ventas_globales.values(
        'detalles__boleto__evento__nombre'
    ).annotate(
        ganancias=Sum('ganancia_proveedor', distinct=True)
    ).order_by('-ganancias')[:5]
    labels_top_eventos = [e['detalles__boleto__evento__nombre'] for e in ganancias_por_evento_qs]
    data_top_eventos = [float(e['ganancias']) for e in ganancias_por_evento_qs]

    ultimas_ventas = ventas_globales.order_by('-fecha_compra')[:5]
    eventos_list = eventos_proveedor.select_related('categoria').order_by('-creado_en')

    paginator = Paginator(eventos_list, 10)
    page_number = request.GET.get('page')
    page_obj_eventos = paginator.get_page(page_number)
    page_obj_eventos.object_list = _attach_event_stats(list(page_obj_eventos.object_list))

    context = {
        'ganancias_totales': ganancias_totales,
        'ganancias_30_dias': ganancias_30_dias,
        'eventos_publicados_count': eventos_publicados_count, 
        'ganancia_promedio_evento': ganancia_promedio_evento,
        'labels_ingresos_mes': json.dumps(labels_ingresos_mes), 
        'data_ingresos_mes': json.dumps(data_ingresos_mes),
        'labels_top_eventos': json.dumps(labels_top_eventos), 
        'data_top_eventos': json.dumps(data_top_eventos),
        'ultimas_ventas': ultimas_ventas, 
        'eventos_activos': page_obj_eventos,
    }
    return render(request, 'tickets/panel_proveedor.html', context)


@login_required
def filtrar_eventos_proveedor_ajax(request):
    eventos_list = Evento.objects.filter(creado_por=request.user).select_related('categoria').order_by('-creado_en')
    paginator = Paginator(eventos_list, 10)
    page_number = request.GET.get('page')
    page_obj_eventos = paginator.get_page(page_number)
    page_obj_eventos.object_list = _attach_event_stats(list(page_obj_eventos.object_list))
    context = {'eventos_activos': page_obj_eventos}
    return render(request, 'tickets/panel_proveedor_tabla_ajax.html', context)

# ======================================================
# === Vistas de Administración (para eventos)
# ======================================================

@admin_required
def gestion_eventos(request):
    eventos = Evento.objects.all().order_by('-fecha')
    context = {'eventos': eventos}
    return render(request, 'tickets/gestion_eventos.html', context)

@admin_required
def lista_eventos_pendientes(request):
    eventos_qs = Evento.objects.filter(aprobado=False).select_related('creado_por', 'categoria').order_by('-creado_en')
    paginator = Paginator(eventos_qs, 25)  # 25 eventos por página
    page_number = request.GET.get('page')
    eventos_pendientes = paginator.get_page(page_number)
    context = {
        'eventos': eventos_pendientes,
        'panel_title': 'Eventos Pendientes de Aprobación',
        'panel_subtitle': 'Revisa y aprueba/rechaza los eventos enviados por proveedores.'
    }
    return render(request, 'tickets/lista_eventos_pendientes.html', context)

@admin_required
def aprobar_evento(request, evento_id):
    if request.method == 'POST':
        evento = get_object_or_404(Evento, pk=evento_id)
        evento.aprobado = True
        evento.save()
        messages.success(request, f'El evento "{evento.nombre}" ha sido aprobado.')
        if evento.creado_por:
            notification_link = reverse('tickets:detalle_evento', args=[evento.id])
            create_web_notification(
                evento.creado_por, 'evento_aprobado', f'¡Tu evento "{evento.nombre}" ha sido aprobado!', link=notification_link
            )
        return redirect('tickets:lista_eventos_pendientes')

@admin_required
def rechazar_evento(request, evento_id):
    if request.method == 'POST':
        evento = get_object_or_404(Evento, pk=evento_id)
        evento_nombre = evento.nombre
        if evento.creado_por:
            create_web_notification(
                evento.creado_por, 'evento_rechazado', f'Tu evento "{evento_nombre}" ha sido rechazado.',
                link=reverse('tickets:panel_proveedor')
            )
        evento.delete()
        messages.warning(request, f'El evento "{evento_nombre}" ha sido rechazado y eliminado.')
    return redirect('tickets:lista_eventos_pendientes')

@login_required
@require_POST
def toggle_favorito_view(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    usuario = request.user
    message_text = ""
    if evento in usuario.eventos_favoritos.all():
        usuario.eventos_favoritos.remove(evento)
        message_text = f"'{evento.nombre}' eliminado de tus favoritos."
        is_favorited_now = False
    else:
        usuario.eventos_favoritos.add(evento)
        message_text = f"'{evento.nombre}' añadido a tus favoritos."
        is_favorited_now = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'is_favorited': is_favorited_now, 'message': message_text})
    else:
        messages.success(request, message_text)
        return redirect('tickets:detalle_evento', evento_id=evento.id)

@login_required
def get_admin_notification_count_json(request):
    """
    Devuelve el conteo de notificaciones de admin no leídas para el usuario actual como JSON.
    """
    from tickets.utils import get_unread_admin_notifications_count # Importar aquí para evitar circularidad

    count = get_unread_admin_notifications_count(request)
    return JsonResponse({'count': count})

@login_required
def get_pending_events_count_json(request):
    """
    Devuelve el conteo de eventos pendientes de aprobación como JSON.
    """
    # Importamos aquí para evitar problemas de circularidad en los imports
    from tickets.utils import get_pending_events_count
    count = get_pending_events_count()
    return JsonResponse({'count': count})

@login_required
def get_pending_supplier_requests_count_json(request):
    """
    Devuelve el conteo de solicitudes de proveedor pendientes como JSON.
    """
    # Importamos aquí para evitar problemas de circularidad en los imports
    from tickets.utils import get_pending_supplier_requests_count
    count = get_pending_supplier_requests_count()
    return JsonResponse({'count': count})