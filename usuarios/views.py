# usuarios/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models import F
import json
from datetime import timedelta
# Importamos los modelos de Django
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.db.models import Prefetch
from django.http import HttpResponse
# Importamos los mensajes de Django
from django.contrib import messages
# Importamos los formularios de Django
from django import forms
from django.shortcuts import render


# Importamos los formularios de usuarios
from .forms import RegistroForm, LoginForm, SolicitudProveedorForm, ReenviarActivacionForm, UserProfileUpdateForm

# Importamos los modelos de usuarios
from .models import SolicitudProveedor, Notification, Usuario # Importamos Notification
from tickets.models import Venta, Evento # Importamos Notification

# Importamos los modelos de la aplicación tickets (importación local para reducir dependencias globales)
# Estos se importarán dentro de las funciones que los necesiten
# from tickets.models import Categoria, Evento, Boleto, Venta, DetalleVenta, MetodoPago, Opinion 

# Decorador personalizado
from .decorators import admin_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse

# Asegúrate de que el modelo de usuario se importe correctamente
User = get_user_model() 

# --- FUNCIÓN AUXILIAR PARA CREAR NOTIFICACIONES ---
def create_web_notification(recipient, notification_type, message, link=None):
    """
    Crea y guarda una notificación web para un usuario.
    """
    Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        message=message,
        link=link
    )


def registro_view(request):
    """
    Gestiona el registro de nuevos usuarios y envía un correo para activar la cuenta.
    """
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Este correo electrónico ya está registrado.')
                return render(request, 'usuarios/registro.html', {'form': form})

            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # --- Lógica para Enviar Correo de Activación ---
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            activation_link = request.build_absolute_uri(
                reverse('usuarios:activar', kwargs={'uidb64': uid, 'token': token})
            )

            mail_subject = 'Activa tu cuenta en Ticket World'
            html_message = render_to_string('usuarios/activar_correo.html', {
                'user': user,
                'activation_link': activation_link,
            })

            email_message = EmailMultiAlternatives(
                subject=mail_subject,
                body=f'Hola {user.username}, activa tu cuenta haciendo clic aquí: {activation_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email_message.attach_alternative(html_message, "text/html")
            email_message.send()

            return redirect('usuarios:registro_exitoso')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def activar_cuenta_view(request, uidb64, token):
    """
    Activa la cuenta del usuario y muestra una página de confirmación.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'usuarios/activacion_exitoso.html')
    else:
        return render(request, 'usuarios/activacion_fallida.html')


def login_view(request):
    """
    Gestiona el inicio de sesión de usuarios.
    """
    if request.user.is_authenticated:
        return redirect('usuarios:inicio')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        username = form.data.get('username')
        password = form.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            return redirect('usuarios:inicio')
        else:
            try:
                user_obj = User.objects.get(username=username)
                if not user_obj.check_password(password):
                    messages.error(request, 'Usuario o contraseña incorrectos. Por favor, inténtalo de nuevo.')
                elif not user_obj.is_active:
                    messages.error(request, 'Tu cuenta no ha sido activada. Por favor, revisa tu correo electrónico.')
                else:
                    messages.error(request, 'Usuario o contraseña incorrectos. Por favor, inténtalo de nuevo.')
            except User.DoesNotExist:
                messages.error(request, 'Usuario o contraseña incorrectos. Por favor, inténtalo de nuevo.')
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})

def reenviar_activacion_view(request):
    if request.method == 'POST':
        form = ReenviarActivacionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.filter(email=email, is_active=False).first()

            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                activation_link = request.build_absolute_uri(
                    reverse('usuarios:activar', kwargs={'uidb64': uid, 'token': token})
                )
                mail_subject = 'Activa tu cuenta en Ticket World'
                html_message = render_to_string('usuarios/activar_correo.html', {
                    'user': user,
                    'activation_link': activation_link,
                })
                email_message = EmailMultiAlternatives(
                    subject=mail_subject,
                    body=f'Hola {user.username}, activa tu cuenta haciendo clic aquí: {activation_link}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
                email_message.attach_alternative(html_message, "text/html")
                email_message.send()

            messages.success(request, '¡Hecho! Si tu correo electrónico está en nuestros registros, recibirás un nuevo enlace de activación en breve.')
            return render(request, 'usuarios/reenviar_activacion.html', {
                'form': ReenviarActivacionForm()
            })
    else:
        form = ReenviarActivacionForm()

    return render(request, 'usuarios/reenviar_activacion.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado tu sesión en Ticket World de forma segura. ¡Vuelve pronto!")
    return redirect('usuarios:despedida')

def despedida_view(request):
    list(messages.get_messages(request)) # Consumir mensajes
    return render(request, 'usuarios/despedida.html')

def registro_exitoso(request):
    return render(request, 'usuarios/registro_exitoso.html')

# -------------------------------------------------------------------
# VISTA 'INICIO' (Página principal de eventos)
# -------------------------------------------------------------------
def inicio(request):
    """
    Muestra la página de inicio con eventos futuros, destacados y lógica de paginación/búsqueda.
    """
    # Importaciones de modelos locales para reducir dependencias globales
    from tickets.models import Categoria, Evento

    eventos_list = Evento.objects.filter(aprobado=True, fecha__gte=timezone.now()).order_by('fecha')
    categorias = Categoria.objects.all()
    categoria_filtrada = None

    # --- Lógica de Filtrado y Búsqueda ---
    categoria_id = request.GET.get('categoria')
    query = request.GET.get('q')

    if categoria_id:
        eventos_list = eventos_list.filter(categoria__id=categoria_id)
        categoria_filtrada = get_object_or_404(Categoria, id=categoria_id)

    if query:
        eventos_list = eventos_list.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(lugar__icontains=query) |
            Q(categoria__nombre__icontains=query) |
            Q(creado_por__username__icontains=query)
        )

    # =======================================================
    # === NUEVA LÓGICA PARA SELECCIONAR EVENTOS DESTACADOS ===
    # =======================================================
    eventos_destacados = Evento.objects.filter(
        aprobado=True,
        fecha__gte=timezone.now()
    ).order_by('fecha')[:3] # Tomamos los 3 eventos más próximos

    # === LÓGICA DE PAGINACIÓN ===
    paginator = Paginator(eventos_list, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # === OBTENER IDs DE EVENTOS FAVORITOS para el contexto ===
    favorited_event_ids = _get_common_event_context(request)

    context = {
        'categorias': categorias,
        'page_obj': page_obj,
        'categoria_filtrada': categoria_filtrada,
        'search_query': query,
        'favorited_event_ids': favorited_event_ids,
        'eventos_destacados': eventos_destacados, # <-- AÑADIDO AL CONTEXTO
    }

    return render(request, 'usuarios/inicio.html', context)

# --- Función auxiliar para obtener eventos favoritos del usuario ---
def _get_common_event_context(request):
    """
    Obtiene los IDs de los eventos favoritos del usuario autenticado.
    """
    # Importación local para evitar dependencia global de Evento en este nivel.
    from tickets.models import Evento 
    favorited_event_ids = set()
    if request.user.is_authenticated:
        # Asegúrate de que el campo en el modelo de usuario sea 'eventos_favoritos'
        favorited_event_ids = set(request.user.eventos_favoritos.values_list('id', flat=True))
    return favorited_event_ids


# --- Función de prueba para el decorador user_passes_test ---
def is_eligible_for_supplier_form(user):
    """
    Verifica si el usuario está autenticado y tiene rol 'usuario' o 'cliente'.
    """
    return user.is_authenticated and (user.rol == 'usuario' or user.rol == 'cliente')


@admin_required
def admin_dashboard(request):
    # --- Métricas para las tarjetas de acción (LÍNEA CORREGIDA) ---
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(aprobado=False).count()
    eventos_pendientes_count = Evento.objects.filter(aprobado=False).count()

    # --- KPIs Globales ---
    hace_30_dias = timezone.now() - timedelta(days=30)
    
    ventas_recientes = Venta.objects.filter(fecha_compra__gte=hace_30_dias, estado='completa')
    ingresos_30_dias = ventas_recientes.aggregate(total=Sum('total_venta'))['total'] or 0
    
    ingresos_totales = Venta.objects.filter(estado='completa').aggregate(total=Sum('total_venta'))['total'] or 0
    
    nuevos_usuarios_30_dias = Usuario.objects.filter(date_joined__gte=hace_30_dias).count()
    total_ventas = Venta.objects.filter(estado='completa').count()

    # --- Datos para Gráfico de Ingresos Diarios ---
    ingresos_diarios = (
        ventas_recientes
        .annotate(dia=TruncDate('fecha_compra'))
        .values('dia')
        .annotate(total=Sum('total_venta'))
        .order_by('dia')
    )
    labels_ingresos = [i['dia'].strftime('%d %b') for i in ingresos_diarios]
    data_ingresos = [float(i['total']) for i in ingresos_diarios]

    # --- Datos para Gráfico de Nuevos Usuarios ---
    usuarios_diarios = (
        Usuario.objects.filter(date_joined__gte=hace_30_dias)
        .annotate(dia=TruncDate('date_joined'))
        .values('dia')
        .annotate(cantidad=Count('id'))
        .order_by('dia')
    )
    labels_usuarios = [u['dia'].strftime('%d %b') for u in usuarios_diarios]
    data_usuarios = [u['cantidad'] for u in usuarios_diarios]
    
    # --- Tablas de Actividad Reciente ---
    ultimas_ventas = Venta.objects.filter(estado='completa').select_related('usuario').order_by('-fecha_compra')[:5]
    ultimos_usuarios = Usuario.objects.order_by('-date_joined')[:5]

    context = {
        'panel_title': 'Panel de Administración',
        'panel_subtitle': 'Un resumen completo del estado y rendimiento de la plataforma.',
        
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'eventos_pendientes_count': eventos_pendientes_count,

        'ingresos_30_dias': ingresos_30_dias,
        'ingresos_totales': ingresos_totales,
        'nuevos_usuarios_30_dias': nuevos_usuarios_30_dias,
        'total_ventas': total_ventas,
        
        'labels_ingresos': json.dumps(labels_ingresos),
        'data_ingresos': json.dumps(data_ingresos),
        'labels_usuarios': json.dumps(labels_usuarios),
        'data_usuarios': json.dumps(data_usuarios),
        
        'ultimas_ventas': ultimas_ventas,
        'ultimos_usuarios': ultimos_usuarios,
    }
    return render(request, 'usuarios/admin_dashboard.html', context)


@user_passes_test(is_eligible_for_supplier_form, login_url=reverse_lazy('usuarios:login'))
def solicitud_proveedor(request):
    """
    Permite a los usuarios con rol 'usuario' o 'cliente' solicitar el rol de proveedor.
    Si ya es proveedor, lo redirige.
    """
    if request.user.rol == 'proveedor':
        messages.info(request, "¡Ya eres un proveedor! Puedes ir a tu panel de eventos para crear/gestionar tus eventos.")
        return redirect('usuarios:perfil')

    if request.method == 'POST':
        form = SolicitudProveedorForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.user = request.user
            solicitud.save()
            messages.success(request, 'Solicitud enviada con éxito, espera la validación por parte de un administrador.')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        initial_data = {
            'nombres': request.user.first_name,
            'apellidos': request.user.last_name,
            'email': request.user.email,
            'telefono': request.user.telefono,
        }
        form = SolicitudProveedorForm(initial=initial_data)

    return render(request, 'usuarios/solicitud_proveedor.html', {'form': form})

@login_required
def perfil(request):
    # Importaciones de modelos locales para la vista de perfil
    from tickets.models import Venta, DetalleVenta, Opinion, Evento 

    # Esto fuerza a que los mensajes sean consumidos de la sesión
    # y así no se muestren de nuevo si no son generados en esta petición
    list(messages.get_messages(request)) 

    # --- Inicialización de formularios ---
    profile_form = UserProfileUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    # --- Inicialización de datos del perfil ---
    # Historial de Compras: Muestra TODAS las ventas completas del usuario
    compras_con_detalles = Venta.objects.filter(usuario=request.user, estado='completa').prefetch_related(
        'detalles__boleto__evento'
    ).order_by('-fecha_compra')
    
    # --- DEBUG LOGS para Compras (comentados para producción) ---
    # print(f"DEBUG: Compras para {request.user.username}: {compras_con_detalles.count()} ventas encontradas.")
    # for compra in compras_con_detalles:
    #     print(f"  Venta ID: {compra.id}, Estado: {compra.estado}, Total: {compra.total_venta}, Fecha: {compra.fecha_compra}")
    #     for detalle in compra.detalles.all():
    #         print(f"    - Detalle: {detalle.cantidad}x {detalle.boleto.display_name} para {detalle.boleto.evento.nombre}")
    # -------------------------------

    # Mis Opiniones
    mis_opiniones = Opinion.objects.filter(usuario=request.user).order_by('-fecha_opinion')

    # Mis Entradas: Muestra boletos para eventos FUTUROS O ACTUALES con venta completa
    mis_entradas_query = DetalleVenta.objects.filter(
        venta__usuario=request.user,
        venta__estado='completa',
        boleto__evento__fecha__gte=timezone.now() # Esta condición filtra por fecha futura
    ).select_related('boleto__evento', 'boleto').order_by('boleto__evento__fecha')

    # --- DEBUG LOGS para Entradas (comentados para producción) ---
    # print(f"DEBUG: Entradas para {request.user.username}: {mis_entradas_query.count()} boletos activos encontrados.")
    # for entrada in mis_entradas_query:
    #     print(f"  - Entrada: {entrada.boleto.display_name} para {entrada.boleto.evento.nombre} (Fecha Evento: {entrada.boleto.evento.fecha})")
    # -------------------------------

    # Agrupar entradas por evento para la plantilla
    eventos_con_entradas = {}
    for detalle in mis_entradas_query:
        evento = detalle.boleto.evento
        if evento.id not in eventos_con_entradas:
            eventos_con_entradas[evento.id] = {
                'evento': evento,
                'boletos_comprados': []
            }
        eventos_con_entradas[evento.id]['boletos_comprados'].append({
            'tipo': detalle.boleto.display_name,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.precio_unitario,
        })
    mis_entradas_para_template = list(eventos_con_entradas.values())

    # Eventos Favoritos
    eventos_favoritos = request.user.eventos_favoritos.all().order_by('nombre')
    
    # --- Lógica de manejo de POST (actualización de perfil/contraseña) ---
    if request.method == 'POST' and 'update_profile' in request.POST:
        profile_form = UserProfileUpdateForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Tu información de perfil ha sido actualizada.')
            create_web_notification(
                request.user,
                'perfil_actualizado',
                'Tu información de perfil ha sido actualizada exitosamente.',
                link=reverse('usuarios:perfil') + '#info-personal'
            )
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Hubo un error al actualizar tu perfil. Por favor, corrige los errores.')
            password_form = PasswordChangeForm(request.user) # Asegurarse de que el password_form exista en el contexto

    elif request.method == 'POST' and 'change_password' in request.POST:
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña ha sido actualizada con éxito.')
            create_web_notification(
                request.user,
                'perfil_actualizado',
                'Tu contraseña ha sido actualizada exitosamente.',
                link=reverse('usuarios:perfil') + '#info-personal'
            )
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Hubo un error al cambiar tu contraseña. Por favor, verifica tu contraseña actual y la nueva.')
            profile_form = UserProfileUpdateForm(instance=request.user) # Asegurarse de que el profile_form exista en el contexto

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'compras': compras_con_detalles,
        'mis_opiniones': mis_opiniones,
        'mis_entradas': mis_entradas_para_template,
        'eventos_favoritos': eventos_favoritos,
        'notifications': Notification.objects.filter(recipient=request.user).order_by('-created_at')
    }
    return render(request, 'usuarios/perfil.html', context)


# --- Vistas de Administración ---

@admin_required
def lista_solicitudes(request):
    solicitudes = SolicitudProveedor.objects.filter(aprobado=False)
    return render(request, 'usuarios/lista_solicitudes.html', {'solicitudes': solicitudes})


@admin_required
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudProveedor, pk=solicitud_id)
    if request.method == 'POST':
        solicitud.aprobado = True
        solicitud.save()
        solicitud.user.rol = 'proveedor'
        solicitud.user.save(update_fields=['rol'])
        messages.success(request, f'Solicitud de {solicitud.user.username} aprobada correctamente. El usuario ahora es proveedor.')
        create_web_notification(
            solicitud.user,
            'solicitud_aprobada',
            f'¡Tu solicitud para ser proveedor ha sido aprobada! Ahora puedes crear eventos.',
            link=reverse('tickets:mis_eventos')
        )
        return redirect('usuarios:lista_solicitudes')
    return render(request, 'usuarios/aprobar_solicitud.html', {'solicitud': solicitud})

@admin_required
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudProveedor, pk=solicitud_id)
    if request.method == 'POST':
        create_web_notification(
            solicitud.user,
            'solicitud_rechazada',
            'Lamentamos informarte que tu solicitud para ser proveedor ha sido rechazada.',
            link=reverse('usuarios:solicitud_proveedor')
        )
        solicitud.delete()
        messages.success(request, f'Solicitud de {solicitud.user.username} rechazada y eliminada.')
        return redirect('usuarios:lista_solicitudes')
    return redirect('usuarios:lista_solicitudes')


@login_required
def notification_list_view(request):
    """
    Muestra la lista de notificaciones del usuario.
    """
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    # Opcional: Marcar todas como leídas al visitar la página (descomentar si se desea)
    # Notification.objects.filter(recipient=request.user, read=False).update(read=True)
    context = {
        'notifications': notifications,
    }
    return render(request, 'usuarios/notifications_list.html', context)


@login_required
@require_POST
def mark_notification_as_read_view(request):
    """
    Marca notificaciones como leídas (individualmente o todas).
    """
    notification_id = request.POST.get('notification_id')
    mark_all = request.POST.get('mark_all')

    if mark_all:
        Notification.objects.filter(recipient=request.user, read=False).update(read=True)
        messages.success(request, 'Todas tus notificaciones han sido marcadas como leídas.') # Este mensaje es el que puede aparecer
    elif notification_id:
        try:
            notification = Notification.objects.get(id=notification_id, recipient=request.user)
            notification.read = True
            notification.save()
            messages.success(request, 'Notificación marcada como leída.') # Este mensaje es el que puede aparecer
        except Notification.DoesNotExist:
            messages.error(request, 'Notificación no encontrada o no tienes permiso para marcarla como leída.')
    else:
        messages.error(request, 'Solicitud inválida.')
    
    return JsonResponse({'status': 'success'})


@login_required
def get_unread_notifications_count(request):
    """
    Devuelve el conteo de notificaciones no leídas para el usuario actual.
    """
    count = Notification.objects.filter(recipient=request.user, read=False).count()
    return JsonResponse({'unread_count': count})