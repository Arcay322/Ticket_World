# tickets/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Evento, AdminNotification
from usuarios.models import SolicitudProveedor
from django.contrib.auth import get_user_model # <-- ¡Añade esta importación!

# Señal para notificar sobre Eventos Pendientes de Aprobación
@receiver(post_save, sender=Evento)
def event_approval_notification_admin(sender, instance, created, **kwargs):
    if created and not instance.aprobado:
        # --- ¡CORRECCIÓN AQUÍ! ---
        User = get_user_model() # Obtiene la CLASE del modelo de usuario
        admin_users = User.objects.filter(is_superuser=True) # Ahora sí puedes consultar
        # --- FIN CORRECCIÓN ---

        for admin_user in admin_users:
            AdminNotification.objects.create(
                recipient=admin_user,
                type='aprobacion_evento',
                message=f'El evento "{instance.nombre}" ha sido creado y requiere tu aprobación.',
                link=f'/admin/tickets/evento/{instance.pk}/change/',
                created_at=instance.creado_en
            )

# Señal para notificar sobre Solicitudes de Proveedores Pendientes
@receiver(post_save, sender=SolicitudProveedor)
def supplier_request_approval_notification_admin(sender, instance, created, **kwargs):
    if created and not instance.aprobado:
        # --- ¡CORRECCIÓN AQUÍ! ---
        User = get_user_model() # Obtiene la CLASE del modelo de usuario
        admin_users = User.objects.filter(is_superuser=True) # Ahora sí puedes consultar
        # --- FIN CORRECCIÓN ---

        for admin_user in admin_users:
            AdminNotification.objects.create(
                recipient=admin_user,
                type='solicitud_proveedor',
                message=f'Nueva solicitud de proveedor de {instance.nombres} {instance.apellidos} pendiente de aprobación.',
                link=f'/admin/usuarios/solicitudproveedor/{instance.pk}/change/',
                created_at=instance.fecha_solicitud
            )