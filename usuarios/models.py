# usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UsuarioManager

class Usuario(AbstractUser):
    ROL_CHOICES = (
        ('usuario', 'Usuario'),   # <-- AÑADIMOS EL NUEVO ROL
        ('cliente', 'Cliente'),
        ('proveedor', 'Proveedor'),
        ('admin', 'Administrador'),
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='usuario')

    # Campos adicionales
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    foto_perfil = models.ImageField(upload_to='perfil/', blank=True, null=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.username


class SolicitudProveedor(models.Model):
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    nombre_empresa = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.nombre_empresa}"