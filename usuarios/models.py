# usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
# from .managers import UsuarioManager # Comentado si no se está usando un manager personalizado
from django.utils import timezone
from django.conf import settings # ¡IMPORTANTE: Importar settings para AUTH_USER_MODEL!

# ¡IMPORTANTE!: Importa el modelo Evento desde la aplicación tickets
# Aunque Evento importa a Usuario, al usar settings.AUTH_USER_MODEL como string,
# la circularidad debería resolverse correctamente en Django.
from tickets.models import Evento 


class Usuario(AbstractUser):
    # Usamos mayúsculas por convención para las tuplas de choices
    ROL_CHOICES = [
        ('usuario', 'Usuario'),
        ('cliente', 'Cliente'),
        ('proveedor', 'Proveedor'),
        ('admin', 'Administrador'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='usuario')
    
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Sobre mí")

    # Campo de favoritos: Usamos el modelo Evento directamente
    eventos_favoritos = models.ManyToManyField(
        Evento,
        related_name='favorited_by',
        blank=True,
        verbose_name="Eventos Favoritos"
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta(AbstractUser.Meta):
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['username']

    def __str__(self):
        return self.username

class SolicitudProveedor(models.Model):
    # Usar settings.AUTH_USER_MODEL como string para relaciones al modelo de usuario personalizado
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitudes_proveedor_recibidas')
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    nombre_empresa = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Solicitud de Proveedor"
        verbose_name_plural = "Solicitudes de Proveedores"
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.nombre_empresa}"

class Notification(models.Model):
    # Destinatario de la notificación: Usar settings.AUTH_USER_MODEL como string
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='web_notifications', verbose_name="Destinatario")
    
    # Tipo de notificación para categorización
    NOTIFICATION_TYPES = [
        ('compra', 'Confirmación de Compra'),
        ('evento_favorito', 'Actualización de Evento Favorito'),
        ('evento_aprobado', 'Evento Aprobado'),
        ('evento_rechazado', 'Evento Rechazado'),
        ('solicitud_aprobada', 'Solicitud de Proveedor Aprobada'),
        ('solicitud_rechazada', 'Solicitud de Proveedor Rechazada'),
        ('perfil_actualizado', 'Perfil Actualizado'),
        ('general', 'General'),
        ('recordatorio_evento', 'Recordatorio de Evento'),
    ]
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='general', verbose_name="Tipo de Notificación")
    
    message = models.TextField(verbose_name="Mensaje")
    
    # URL opcional a donde redirigir al usuario al hacer clic en la notificación
    link = models.URLField(max_length=500, blank=True, null=True, verbose_name="Enlace Relacionado")
    
    # Estado de lectura
    read = models.BooleanField(default=False, verbose_name="Leída")
    
    # Marca de tiempo de creación
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-created_at'] # Las más nuevas primero

    def __str__(self):
        return f"[{self.get_notification_type_display()}] para {self.recipient.username}: {self.message[:50]}..."
