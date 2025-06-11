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
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone

# Importamos los formularios y modelos necesarios
from .forms import RegistroForm, LoginForm, PerfilForm, SolicitudProveedorForm, ReenviarActivacionForm
from .models import SolicitudProveedor,Usuario

# Modelos de la otra app para la página de inicio
from tickets.models import Categoria, Evento

# Decorador personalizado
from .decorators import admin_required

# Modelo de Usuario personalizado
Usuario = get_user_model()


def registro_view(request):
    """
    Gestiona el registro de nuevos usuarios y envía un correo para activar la cuenta.
    """
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if Usuario.objects.filter(email=email).exists():
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
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # La cuenta es válida, la activamos
        user.is_active = True
        user.save()

        # Mostramos la página de activación exitosa.
        return render(request, 'usuarios/activacion_exitosa.html')
    else:
        # El enlace no es válido, mostramos la página de fallo.
        return render(request, 'usuarios/activacion_fallida.html')


def login_view(request):
    """
    Versión definitiva de login que comprueba manualmente al usuario
    para dar mensajes de error específicos y correctos.
    """
    if request.user.is_authenticated:
        return redirect('usuarios:inicio')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        # Obtenemos el usuario y la contraseña del formulario enviado
        username = form.data.get('username')
        password = form.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            return redirect('usuarios:inicio')
        else:
            try:
                user_obj = Usuario.objects.get(username=username)

                if not user_obj.check_password(password):
                    messages.error(request, 'Usuario o contraseña incorrectos. Por favor, inténtalo de nuevo.')
                elif not user_obj.is_active:
                    messages.error(request, 'Tu cuenta no ha sido activada. Por favor, revisa tu correo electrónico.')
                else:
                    messages.error(request, 'Usuario o contraseña incorrectos. Por favor, inténtalo de nuevo.')

            except Usuario.DoesNotExist:
                messages.error(request, 'Usuario o contraseña incorrectos. Por favor, inténtalo de nuevo.')
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})

def reenviar_activacion_view(request):
    if request.method == 'POST':
        form = ReenviarActivacionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = Usuario.objects.filter(email=email, is_active=False).first()

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

# -------------------------------------------------------------------
# VISTA 'INICIO' CORREGIDA Y DINÁMICA
# -------------------------------------------------------------------
def inicio(request):
    """
    Muestra la página de inicio con una lista de categorías y eventos.
    Ahora solo muestra eventos aprobados y futuros.
    """
    # --- TEMPORAL: LÍNEAS DE DEPURACIÓN EN VISTA INICIO ---
    current_datetime = timezone.now()
    print(f"\n--- DEBUG EN VISTA 'inicio' ---")
    print(f"Hora actual (timezone.now()): {current_datetime}")

    # Filtramos eventos: aprobados, con fecha mayor o igual a la actual
    eventos_filtrados = Evento.objects.filter(
        aprobado=True,
        fecha__gte=current_datetime
    ).order_by('fecha')

    print(f"Eventos recuperados para la página de inicio ({len(eventos_filtrados)} encontrados):")
    for evento in eventos_filtrados:
        print(f"  - ID: {evento.id}, Nombre: '{evento.nombre}', Aprobado: {evento.aprobado}, Fecha: {evento.fecha}, Es Futuro: {evento.fecha > current_datetime}")
    print(f"--- FIN DEBUG VISTA 'inicio' ---\n")
    # --- FIN DE LÍNEAS DE DEPURACIÓN ---

    categorias = Categoria.objects.all()

    context = {
        'categorias': categorias,
        'eventos': eventos_filtrados, # Pasamos la variable con los eventos filtrados
    }
    
    return render(request, 'usuarios/inicio.html', context)
    
# --- Función de prueba para el decorador user_passes_test ---
def is_eligible_for_supplier_form(user):
    """
    Verifica si el usuario está autenticado y tiene rol 'usuario' o 'cliente'.
    """
    return user.is_authenticated and (user.rol == 'usuario' or user.rol == 'cliente')

# ¡ELIMINAMOS EL DECORADOR @user_passes_test DE AQUÍ!
@admin_required
def admin_dashboard(request):
    # --- TEMPORAL: LÍNEAS DE DEPURACIÓN (Mantenemos por ahora para confirmar) ---
    print(f"\n--- DEBUG EN admin_dashboard ---")
    print(f"URL solicitada: {request.path}")
    print(f"Usuario autenticado?: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        print(f"Rol del usuario autenticado: {request.user.rol}")
    else:
        print(f"Usuario NO autenticado. Esto NO debería pasar si el login_required funciona.")
    print(f"--- FIN DEBUG ---\n")
    # --- FIN DE LÍNEAS DE DEPURACIÓN ---

    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(aprobado=False).count()
    eventos_pendientes_count = Evento.objects.filter(aprobado=False).count()

    total_usuarios = Usuario.objects.count()
    total_proveedores = Usuario.objects.filter(rol='proveedor').count()
    total_clientes = Usuario.objects.filter(rol='cliente').count()
    total_admins = Usuario.objects.filter(rol='admin').count()
    total_normal_users = Usuario.objects.filter(rol='usuario').count()

    context = {
        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'eventos_pendientes_count': eventos_pendientes_count,
        'total_usuarios': total_usuarios,
        'total_proveedores': total_proveedores,
        'total_clientes': total_clientes,
        'total_admins': total_admins,
        'total_normal_users': total_normal_users,
        'panel_title': 'Panel de Administración',
        'panel_subtitle': 'Resumen y acceso rápido a la gestión de la plataforma.',
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
def perfil_usuario(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Perfil actualizado con éxito!')
            return redirect('usuarios:perfil')
    else:
        form = PerfilForm(instance=request.user)

    return render(request, 'usuarios/perfil.html', {'form': form, 'usuario': request.user})


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
        return redirect('usuarios:lista_solicitudes')
    return render(request, 'usuarios/aprobar_solicitud.html', {'solicitud': solicitud})


@admin_required
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudProveedor, pk=solicitud_id)
    if request.method == 'POST':
        solicitud.delete()
        messages.success(request, f'Solicitud de {solicitud.user.username} rechazada y eliminada.')
        return redirect('usuarios:lista_solicitudes')
    return redirect('usuarios:lista_solicitudes')
