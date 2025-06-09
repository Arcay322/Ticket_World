# tickets/models.py

from django.db import models
from django.conf import settings # <-- IMPORTANTE

class Categoria(models.Model):
    nombre = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre

class Evento(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField()
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='eventos')
    lugar = models.CharField(max_length=250, blank=True, null=True)
    def __str__(self):
        return self.nombre

class Boleto(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='boletos')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()
    def __str__(self):
        return f"{self.evento.nombre} - ${self.precio}"

class MetodoPago(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre

# LA CLASE 'Usuario' DEBE SER ELIMINADA DE ESTE ARCHIVO

class Venta(models.Model):
    # Usamos el modelo de usuario correcto de todo el proyecto
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ventas')
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, related_name='ventas')
    fecha_compra = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Venta #{self.pk} - {self.usuario.email} - {self.fecha_compra}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    boleto = models.ForeignKey(Boleto, on_delete=models.PROTECT, related_name='detalle_ventas')
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.cantidad} x {self.boleto} en venta {self.venta.pk}"

class Opinion(models.Model):
    # Usamos el modelo de usuario correcto de todo el proyecto
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='opiniones')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='opiniones')
    calificacion = models.IntegerField(blank=True, null=True)
    comentario = models.TextField(blank=True, null=True)
    fecha_opinion = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Opinion de {self.usuario.email} sobre {self.evento.nombre}"