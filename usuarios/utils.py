# usuarios/utils.py
from django.core.signing import TimestampSigner
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string

signer = TimestampSigner()

def enviar_correo_activacion(request, user):
    token = signer.sign(user.pk)
    url_confirmacion = request.build_absolute_uri(
        reverse('confirmar_correo', args=[token])
    )

    # Asunto del correo
    asunto = 'Activa tu cuenta en Ticket World'

    # Renderizamos el HTML del correo
    mensaje_html = render_to_string('usuarios/activar_correo.html', {
        'user': user,
        'url_confirmacion': url_confirmacion,
        'request': request
    })

    # EmailMultiAlternatives para soportar HTML
    email = EmailMultiAlternatives(
        subject=asunto,
        body='Activa tu cuenta en Ticket World usando el siguiente enlace: ' + url_confirmacion,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )

    # Adjuntar versión HTML
    email.attach_alternative(mensaje_html, "text/html")

    # Enviar el correo
    email.send()
