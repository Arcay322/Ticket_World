import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, F
from decimal import Decimal
from datetime import timedelta

class Categoria(models.Model):
    nombre = models.CharField(max_length=255, unique=True, verbose_name="Nombre de la Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Evento(models.Model):
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos_creados', verbose_name="Creado por")
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Evento")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción Detallada")
    fecha = models.DateTimeField(verbose_name="Fecha y Hora del Evento")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='eventos', verbose_name="Categoría")
    imagen_portada = models.ImageField(upload_to='eventos/', blank=True, null=True, verbose_name="Imagen de Portada")

    # ===================================================================
    # === CAMPOS DE UBICACIÓN PARA INTEGRACIÓN CON MAPAS ===
    # ===================================================================
    lugar_nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del Lugar o Recinto",
        help_text="Ej: Estadio Nacional, Centro de Convenciones",
        blank=True,
        null=True
    )
    direccion = models.CharField(
        max_length=255,
        verbose_name="Dirección Completa",
        help_text="Ej: Av. José Díaz s/n, Cercado de Lima",
        blank=True,
        null=True
    )
    ciudad = models.CharField(
        max_length=100,
        verbose_name="Ciudad",
        help_text="Ej: Lima, Arequipa, Bogotá",
        blank=True,
        null=True
    )
    pais = models.CharField(
        max_length=100,
        verbose_name="País",
        help_text="Ej: Perú, Colombia, Argentina",
        blank=True,
        null=True
    )
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name="Latitud",
        help_text="Coordenada geográfica de latitud para el mapa (ej: -12.0464)."
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name="Longitud",
        help_text="Coordenada geográfica de longitud para el mapa (ej: -77.0428)."
    )
    mapa_enlace_embed = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Enlace de Mapa Incrustado",
        help_text="URL generada para incrustar el mapa de la ubicación del evento (iframe)."
    )
    # ===================================================================
    # === FIN DE CAMPOS DE UBICACIÓN ===
    # ===================================================================

    aprobado = models.BooleanField(default=False, verbose_name="Aprobado por Admin", help_text="Indica si el evento ha sido revisado y aprobado por un administrador.")
    esta_activo = models.BooleanField(default=True, verbose_name="Activo y Visible", help_text="Controla si el evento está visible en el sitio (aunque esté aprobado).")
    esta_agotado = models.BooleanField(default=False, verbose_name="Boletos Agotados", help_text="Se marca automáticamente si no quedan boletos disponibles.")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    es_destacado = models.BooleanField(default=False, verbose_name="Es Destacado", help_text="Marca este evento para que aparezca en la sección de destacados.")

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['fecha']
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'fecha'], name='evento_unico_por_nombre_y_fecha')
        ]

    def __str__(self):
        return f"{self.nombre} ({self.categoria.nombre})"

    @property
    def es_futuro(self):
        return self.fecha > timezone.now()

    @property
    def show_countdown(self):
        now = timezone.now()
        one_month_from_now = now + timedelta(days=30)
        return self.fecha > now and self.fecha <= one_month_from_now

    @property
    def total_boletos_vendidos(self):
        total = self.boletos.aggregate(total=Sum('cantidad_vendida'))['total']
        return total or 0

    @property
    def ingresos_generados(self):
        total = self.boletos.aggregate(
            total=Sum(F('detalle_ventas__cantidad') * F('detalle_ventas__precio_unitario'))
        )['total']
        return total or Decimal('0.00')

class Boleto(models.Model):
    TIPO_BOLETO_CHOICES = [
        ('general', 'General'), ('vip', 'VIP'), ('preventa', 'Preventa'),
        ('estudiante', 'Estudiante'), ('conadis', 'CONADIS'), ('otro', 'Otro'),
    ]
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='boletos', verbose_name="Evento")
    tipo = models.CharField(max_length=50, choices=TIPO_BOLETO_CHOICES, default='general', verbose_name="Tipo de Boleto")
    nombre_boleto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre del Boleto", help_text="Ej: 'Entrada General Día 1', 'Mesa VIP', etc.")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    cantidad_total = models.PositiveIntegerField(verbose_name="Cantidad Total Disponible")
    cantidad_vendida = models.PositiveIntegerField(default=0, verbose_name="Cantidad Vendida")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    @property
    def display_name(self):
        return self.nombre_boleto if self.nombre_boleto else self.get_tipo_display()

    class Meta:
        verbose_name = "Boleto"
        verbose_name_plural = "Boletos"
        unique_together = ('evento', 'tipo', 'nombre_boleto')
        ordering = ['precio']

    def __str__(self):
        return f"{self.display_name} para {self.evento.nombre} (${self.precio})"

    @property
    def cantidad_restante(self):
        return self.cantidad_total - self.cantidad_vendida

    @property
    def esta_agotado(self):
        return self.cantidad_restante <= 0

class MetodoPago(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Método de Pago")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
        
    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        ordering = ['nombre']

class Venta(models.Model):
    ESTADO_VENTA_CHOICES = [
        ('pendiente', 'Pendiente'), ('completa', 'Completa'),
        ('cancelada', 'Cancelada'), ('reembolsada', 'Reembolsada'),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ventas', verbose_name="Usuario")
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, related_name='ventas', verbose_name="Método de Pago")
    fecha_compra = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Compra")
    
    total_bruto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Bruto de la Venta")
    comision_plataforma = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Comisión de la Plataforma")
    ganancia_proveedor = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Ganancia para el Proveedor")

    estado = models.CharField(max_length=20, choices=ESTADO_VENTA_CHOICES, default='pendiente', verbose_name="Estado de la Venta")
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_compra']

    def __str__(self):
        return f"Venta #{self.pk} - {self.usuario.username} - {self.total_bruto} ({self.get_estado_display()})"

class DetalleVenta(models.Model):
    boleto_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles', verbose_name="Venta")
    boleto = models.ForeignKey(Boleto, on_delete=models.PROTECT, related_name='detalle_ventas', verbose_name="Boleto")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario al Momento de la Venta")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Ventas"
        unique_together = ('venta', 'boleto')

    def __str__(self):
        return f"{self.cantidad} x {self.boleto.display_name} en venta {self.venta.pk}"

class Opinion(models.Model):
    ESTADO_OPINION_CHOICES = [
        ('pendiente', 'Pendiente'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada'),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='opiniones', verbose_name="Usuario")
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='opiniones', verbose_name="Evento")
    calificacion = models.IntegerField(blank=True, null=True, choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Calificación")
    comentario = models.TextField(blank=True, null=True, verbose_name="Comentario")
    estado = models.CharField(max_length=20, choices=ESTADO_OPINION_CHOICES, default='pendiente', verbose_name="Estado de Moderación")
    fecha_opinion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Opinión")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Opinión"
        verbose_name_plural = "Opiniones"
        ordering = ['-fecha_opinion']
        unique_together = ('usuario', 'evento')

    def __str__(self):
        return f"Opinión de {self.usuario.username} sobre {self.evento.nombre} (Calificación: {self.calificacion})"

class AdminNotification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_notifications', 
        verbose_name="Destinatario Admin",
        limit_choices_to={'is_superuser': True}
    )

    NOTIFICATION_TYPES = [
        ('aprobacion_evento', 'Aprobación de Evento'),
        ('solicitud_proveedor', 'Solicitud de Proveedor'),
        ('comentario_pendiente', 'Comentario Pendiente'),
        ('error_sistema', 'Error del Sistema'),
        ('general', 'General Admin'),
    ]
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='general', verbose_name="Tipo")
    message = models.TextField(verbose_name="Mensaje")
    link = models.URLField(max_length=500, blank=True, null=True, verbose_name="Enlace Admin")
    read = models.BooleanField(default=False, verbose_name="Leída")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Notificación de Admin"
        verbose_name_plural = "Notificaciones de Admin"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_type_display()}] para {self.recipient.username}: {self.message[:50]}..."