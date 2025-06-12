# tickets/models.py

from django.db import models
from django.conf import settings 
from django.utils import timezone

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
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='eventos_creados',
        null=True, blank=True,
        verbose_name="Creado por"
    )
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Evento")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción Detallada")
    fecha = models.DateTimeField(verbose_name="Fecha y Hora del Evento")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='eventos', verbose_name="Categoría")
    lugar = models.CharField(max_length=250, blank=True, null=True, verbose_name="Lugar del Evento")
    direccion = models.CharField(max_length=500, blank=True, null=True, verbose_name="Dirección Completa")
    imagen_portada = models.ImageField(upload_to='eventos/', blank=True, null=True, verbose_name="Imagen de Portada")
    aprobado = models.BooleanField(default=False, verbose_name="Aprobado por Admin",
                                  help_text="Indica si el evento ha sido revisado y aprobado por un administrador.")
    esta_activo = models.BooleanField(default=True, verbose_name="Activo y Visible",
                                      help_text="Controla si el evento está visible en el sitio (aunque esté aprobado).")
    esta_agotado = models.BooleanField(default=False, verbose_name="Boletos Agotados",
                                       help_text="Se marca automáticamente si no quedan boletos disponibles.")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['fecha']
        
        # === CAMBIO 1: REGLA PARA EVITAR EVENTOS DUPLICADOS ===
        # Le dice a la base de datos que no permita dos entradas
        # con el mismo nombre Y la misma fecha.
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'fecha'], name='evento_unico_por_nombre_y_fecha')
        ]

    def __str__(self):
        return f"{self.nombre} ({self.categoria.nombre})"

    @property
    def es_futuro(self):
        return self.fecha > timezone.now()
        
class Boleto(models.Model):
    TIPO_BOLETO_CHOICES = [
        ('general', 'General'),
        ('vip', 'VIP'),
        ('preventa', 'Preventa'),
        ('estudiante', 'Estudiante'),
        ('conadis', 'CONADIS'),
        ('otro', 'Otro'),
    ]

    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='boletos', verbose_name="Evento")
    tipo = models.CharField(max_length=50, choices=TIPO_BOLETO_CHOICES, default='general', verbose_name="Tipo de Boleto")
    nombre_boleto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre del Boleto",
                                     help_text="Ej: 'Entrada General Día 1', 'Mesa VIP', etc.")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    cantidad_total = models.PositiveIntegerField(verbose_name="Cantidad Total Disponible")
    cantidad_vendida = models.PositiveIntegerField(default=0, verbose_name="Cantidad Vendida")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    # === MÉTODO AÑADIDO: Esta es la nueva propiedad inteligente ===
    @property
    def display_name(self):
        # Si 'nombre_boleto' tiene texto, lo devuelve. Si no, devuelve el nombre legible del 'tipo'.
        return self.nombre_boleto if self.nombre_boleto else self.get_tipo_display()

    class Meta:
        verbose_name = "Boleto"
        verbose_name_plural = "Boletos"
        unique_together = ('evento', 'tipo', 'nombre_boleto')
        ordering = ['precio']

    def __str__(self):
        # Actualizamos el __str__ para que use nuestra nueva propiedad
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

    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Venta(models.Model):
    ESTADO_VENTA_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completa', 'Completa'),
        ('cancelada', 'Cancelada'),
        ('reembolsada', 'Reembolsada'),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ventas', verbose_name="Usuario")
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, related_name='ventas', verbose_name="Método de Pago")
    fecha_compra = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Compra")
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total de la Venta")
    estado = models.CharField(max_length=20, choices=ESTADO_VENTA_CHOICES, default='pendiente', verbose_name="Estado de la Venta")
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_compra']

    def __str__(self):
        return f"Venta #{self.pk} - {self.usuario.username} - {self.total_venta} ({self.get_estado_display()})"
    
    def calcular_total_venta(self):
        total = sum(detalle.precio_unitario * detalle.cantidad for detalle in self.detalles.all())
        self.total_venta = total
        self.save(update_fields=['total_venta'])

class DetalleVenta(models.Model):
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
        return f"{self.cantidad} x {self.boleto.nombre_boleto or self.boleto.get_tipo_display()} en venta {self.venta.pk}"

class Opinion(models.Model):
    ESTADO_OPINION_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
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