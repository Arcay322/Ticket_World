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
from .decorators import admin_required # Correct import for admin_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models import F
import json
from datetime import timedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.db.models import Prefetch
from django.http import JsonResponse, HttpResponse
from django import forms
from django.shortcuts import render
from django.http import HttpRequest

def health_check(request):
    """Una vista simple que no hace nada, para pruebas de despliegue."""
    return HttpResponse("OK")

# Importamos los formularios de usuarios
from .forms import RegistroForm, LoginForm, SolicitudProveedorForm, ReenviarActivacionForm, UserProfileUpdateForm

# --- IMPORTAMOS UserNotification EN LUGAR DE Notification ---
from .models import SolicitudProveedor, UserNotification, Usuario
from tickets.models import Venta, DetalleVenta, Opinion, Evento, Categoria

from django.views.decorators.http import require_POST

User = get_user_model() 

# --- FUNCIÓN AUXILIAR PARA CREAR NOTIFICACIONES (AHORA USA UserNotification) ---
def create_web_notification(recipient, notification_type, message, link=None):
    print(f"DEBUG: create_web_notification: Intentando crear notificación para {recipient.username} (Tipo: {notification_type}).")
    try:
        UserNotification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            message=message,
            link=link
        )
        print(f"DEBUG: create_web_notification: Notificación creada exitosamente para {recipient.username}.")
    except Exception as e:
        print(f"DEBUG: create_web_notification: ERROR al crear notificación para {recipient.username}: {e}")

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
    list(messages.get_messages(request))
    return render(request, 'usuarios/despedida.html')

def registro_exitoso(request):
    return render(request, 'usuarios/registro_exitoso.html')

# --- FUNCIONES AUXILIARES Y VISTAS DE PERFIL / ADMINISTRACIÓN ---

def _get_common_event_context(request):
    """
    Obtiene los IDs de los eventos favoritos del usuario autenticado.
    """
    from tickets.models import Evento # Importación local
    favorited_event_ids = set()
    if request.user.is_authenticated:
        favorited_event_ids = set(request.user.eventos_favoritos.values_list('id', flat=True))
    return favorited_event_ids

def is_eligible_for_supplier_form(user):
    """
    Verifica si el usuario está autenticado y tiene rol 'usuario' o 'cliente'.
    """
    return user.is_authenticated and (user.rol == 'usuario' or user.rol == 'cliente')


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
            link=reverse('tickets:panel_proveedor') # Corregido
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


@login_required
def perfil(request):
    """
    Gestiona la vista de perfil del usuario, incluyendo historial de compras, opiniones, etc.
    """
    list(messages.get_messages(request)) 

    # --- Inicialización de formularios ---
    profile_form = UserProfileUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    # --- Inicialización de datos del perfil (sin paginación) ---
    compras = Venta.objects.filter(usuario=request.user, estado='completa').prefetch_related(
        'detalles__boleto__evento'
    ).order_by('-fecha_compra')

    mis_opiniones = Opinion.objects.filter(usuario=request.user).select_related('evento').order_by('-fecha_opinion')

    # --- ENTRADAS ACTIVAS agrupadas por evento ---
    detalles_entradas = DetalleVenta.objects.filter(
        venta__usuario=request.user,
        venta__estado='completa',
        boleto__evento__fecha__gte=timezone.now()
    ).select_related('boleto__evento', 'boleto').order_by('boleto__evento__fecha')

    entradas_dict = {}
    for detalle in detalles_entradas:
        evento = detalle.boleto.evento
        if evento.id not in entradas_dict:
            entradas_dict[evento.id] = {
                'evento': evento,
                'boletos_comprados': []
            }
        entradas_dict[evento.id]['boletos_comprados'].append({
            'tipo': detalle.boleto.tipo,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.precio_unitario
        })
    mis_entradas = list(entradas_dict.values())

    eventos_favoritos = request.user.eventos_favoritos.select_related('categoria', 'creado_por').order_by('nombre')

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
            password_form = PasswordChangeForm(request.user) 

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
            profile_form = UserProfileUpdateForm(instance=request.user) 

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'compras': compras,
        'mis_opiniones': mis_opiniones,
        'mis_entradas': mis_entradas,
        'eventos_favoritos': eventos_favoritos,
        'notifications': UserNotification.objects.filter(recipient=request.user).order_by('-created_at')
    }
    return render(request, 'usuarios/perfil.html', context)


@login_required
def notification_list_view(request):
    """
    Muestra la lista de notificaciones del usuario.
    """
    notifications = UserNotification.objects.filter(recipient=request.user).order_by('-created_at') # <-- ¡CAMBIADO AQUÍ!
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
        UserNotification.objects.filter(recipient=request.user, read=False).update(read=True) # <-- ¡CAMBIADO AQUÍ!
        messages.success(request, 'Todas tus notificaciones han sido marcadas como leídas.')
    elif notification_id:
        try:
            notification = UserNotification.objects.get(id=notification_id, recipient=request.user) # <-- ¡CAMBIADO AQUÍ!
            notification.read = True
            notification.save()
            messages.success(request, 'Notificación marcada como leída.')
        except UserNotification.DoesNotExist: # <-- ¡CAMBIADO AQUÍ!
            messages.error(request, 'Notificación no encontrada o no tienes permiso para marcarla como leída.')
    else:
        messages.error(request, 'Solicitud inválida.')
    
    return JsonResponse({'status': 'success'})


@login_required
def get_unread_notifications_count(request):
    """
    Devuelve el conteo de notificaciones no leídas para el usuario actual.
    """
    count = UserNotification.objects.filter(recipient=request.user, read=False).count() # <-- ¡CAMBIADO AQUÍ!
    return JsonResponse({'unread_count': count})


# -------------------------------------------------------------------
# VISTA 'INICIO' (Página principal de eventos con lógica de tabs)
# -------------------------------------------------------------------
def inicio(request: HttpRequest):
    """
    Muestra la página de inicio con eventos futuros, destacados y lógica de paginación/búsqueda.
    Maneja la paginación y el cambio de pestañas (tabs) con AJAX.
    """
    categorias = Categoria.objects.all()
    categoria_filtrada = None

    current_tab = request.GET.get('tab', 'proximos')
    categoria_id = request.GET.get('categoria')
    search_query = request.GET.get('q')

    # Queryset base para los eventos principales (paginados)
    eventos_principales_queryset = Evento.objects.filter(aprobado=True, esta_activo=True).select_related('categoria', 'creado_por')

    section_title = "Eventos"

    # 1. Aplicar filtro de búsqueda si existe
    if search_query:
        eventos_principales_queryset = eventos_principales_queryset.filter(
            Q(nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query) |
            Q(lugar_nombre__icontains=search_query) |
            Q(direccion__icontains=search_query) |
            Q(ciudad__icontains=search_query) |
            Q(pais__icontains=search_query) |
            Q(categoria__nombre__icontains=search_query) |
            Q(creado_por__username__icontains=search_query)
        ).distinct()
        section_title = f"Resultados para '{search_query}'"
        current_tab = None
    # 2. Aplicar filtro de categoría si existe (SOLO si no hay búsqueda activa)
    elif categoria_id:
        try:
            categoria_filtrada = get_object_or_404(Categoria, id=categoria_id)
            eventos_principales_queryset = eventos_principales_queryset.filter(categoria=categoria_filtrada)
            section_title = f"Eventos en: {categoria_filtrada.nombre}"
            current_tab = None
        except Exception:
            pass
    # 3. Aplicar lógica de pestañas (SOLO si no hay búsqueda ni filtro de categoría activos)
    if search_query is None and categoria_id is None:
        if current_tab == 'nuevos':
            treinta_dias_atras = timezone.now() - timedelta(days=30)
            eventos_principales_queryset = eventos_principales_queryset.filter(
                creado_en__gte=treinta_dias_atras,
                fecha__gte=timezone.now()
            ).order_by('-creado_en')
            section_title = "Nuevos Eventos"
        else:
            eventos_principales_queryset = eventos_principales_queryset.filter(fecha__gte=timezone.now()).order_by('fecha')
            section_title = "Próximos Eventos"
    else:
        eventos_principales_queryset = eventos_principales_queryset.order_by('fecha')

    # Paginación para los eventos principales
    paginator = Paginator(eventos_principales_queryset, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Eventos "Cerca de Ocurrir"
    eventos_cerca_de_ocurrir = Evento.objects.filter(
        aprobado=True,
        esta_activo=True,
        fecha__gt=timezone.now(),
        fecha__lte=timezone.now() + timedelta(days=7)
    ).select_related('categoria').order_by('fecha')[:4]

    # Eventos Destacados
    eventos_destacados = Evento.objects.filter(
        aprobado=True,
        esta_activo=True,
        es_destacado=True,
        fecha__gte=timezone.now()
    ).select_related('categoria').order_by('?')[:8]

    favorited_event_ids = []
    if request.user.is_authenticated:
        favorited_event_ids = Evento.objects.filter(
            favorited_by=request.user
        ).values_list('id', flat=True)

    context = {
        'categorias': categorias,
        'page_obj': page_obj,
        'categoria_filtrada': categoria_filtrada,
        'search_query': search_query,
        'favorited_event_ids': list(favorited_event_ids),
        'eventos_destacados': eventos_destacados,
        'eventos_cerca_de_ocurrir': eventos_cerca_de_ocurrir,
        'current_tab': current_tab,
        'section_title': section_title,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html_content = render_to_string(
            'tickets/event_list_partial.html',
            context,
            request=request
        )
        return HttpResponse(html_content)
    return render(request, 'usuarios/inicio.html', context)