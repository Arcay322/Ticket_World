from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, get_user_model, logout
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .forms import RegistroForm
from django.core.mail import EmailMultiAlternatives
from .utils import enviar_correo_activacion
from django.contrib import messages
from tickets.models import Evento
import tickets.models
from tickets.models import Venta  # Asegúrate de importar tu modelo de ventas 

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .forms import SolicitudProveedorForm
from .models import SolicitudProveedor
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.decorators import admin_required
from .forms import PerfilForm

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if get_user_model().objects.filter(email=email).exists():
                form.add_error('email', 'Este correo electrónico ya está registrado.')
                return render(request, 'usuarios/registro.html', {'form': form})

            # Crear el usuario pero sin activarlo aún
            user = form.save(commit=False)
            user.is_active = False  # El usuario no estará activo hasta que active su cuenta
            user.save()

            # Enviar el correo de activación
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())
            current_site = get_current_site(request)
            mail_subject = 'Activa tu cuenta en Ticket World'

            # Renderizar el mensaje HTML
            html_message = render_to_string('usuarios/activar_correo.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })

            # Crear el mensaje en texto plano (por compatibilidad)
            text_message = f'Hola {user.username}, confirma tu cuenta haciendo clic aquí: {current_site.domain}/usuarios/activar/{uid}/{token}/'

            # Enviar el correo utilizando EmailMultiAlternatives
            email = EmailMultiAlternatives(mail_subject, text_message, 'from@example.com', [user.email])
            email.attach_alternative(html_message, "text/html")
            email.send()

            # Redirigir a una página de éxito
            return redirect('usuarios:registro_exitoso')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user_model = get_user_model()
        try:
            # Buscar por username o por email
            user = user_model.objects.get(username=username)
        except user_model.DoesNotExist:
            user = None

        if user is not None:
            if not user.is_active:
                return render(request, 'usuarios/login.html', {
                    'error': 'Tu cuenta aún no ha sido activada. Revisa tu correo electrónico.'
                })

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('usuarios:inicio')
            else:
                return render(request, 'usuarios/login.html', {'error': 'Contraseña incorrecta.'})
        else:
            return render(request, 'usuarios/login.html', {'error': 'El usuario no existe.'})

    return render(request, 'usuarios/login.html')



def logout_view(request):
    logout(request)
    return redirect('usuarios:despedida')  # Redirige a la nueva página 'despedida'

def despedida_view(request):
    return render(request, 'usuarios/despedida.html')


def inicio(request):
    return render(request, 'usuarios/inicio.html')

def activar_cuenta_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        Usuario = get_user_model()
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'usuarios/activacion_exitosa.html')
    else:
        return render(request, 'usuarios/activacion_fallida.html')


def registro_exitoso(request):
    return render(request, 'usuarios/registro_exitoso.html')


def reenviar_correo_activacion_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        Usuario = get_user_model()
        try:
            user = Usuario.objects.get(email=email)
            if not user.is_active:
                enviar_correo_activacion(request, user)
                messages.success(request, 'Correo de activación reenviado. Por favor revisa tu bandeja de entrada.')
            else:
                messages.info(request, 'La cuenta ya está activada. Puedes iniciar sesión.')
            return redirect('usuarios:login')
        except Usuario.DoesNotExist:
            messages.error(request, 'No existe una cuenta asociada a ese correo.')
            return redirect('usuarios:reenviar_correo_activacion')
    return render(request, 'usuarios/reenviar_correo_activacion.html')


def solicitud_proveedor(request):
    # Verifica que el usuario sea cliente antes de mostrar el formulario
    if request.user.rol != 'cliente':
        messages.error(request, 'Solo los clientes pueden solicitar el rol de proveedor.')
        return redirect('usuarios:inicio')  # Redirigir a una página principal (ajusta según tu flujo)

    if request.method == 'POST':
        form = SolicitudProveedorForm(request.POST)
        if form.is_valid():
            # Asocia la solicitud con el usuario logueado
            solicitud = form.save(commit=False)
            solicitud.user = request.user
            solicitud.save()

            messages.success(request, 'Solicitud enviada con éxito, espera la validación.')
            return redirect('usuarios:perfil')  # Redirige al perfil del usuario o a otra vista

    else:
        form = SolicitudProveedorForm()

    return render(request, 'usuarios/solicitud_proveedor.html', {'form': form})

@login_required
def perfil_usuario(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('usuarios:perfil')
    else:
        form = PerfilForm(instance=request.user)
    
    return render(request, 'usuarios/perfil.html', {'form': form, 'usuario': request.user})

# Decorador para verificar que el usuario es admin
def admin_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: u.rol == 'admin')(view_func))
    return decorated_view_func

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

        # Cambiar el rol del usuario a proveedor
        solicitud.user.rol = 'proveedor'
        solicitud.user.save()

        messages.success(request, f'Solicitud de {solicitud.user.username} aprobada correctamente.')
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
