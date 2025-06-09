# usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, SolicitudProveedor

# -------------------------------------------------------------------
# CONFIGURACIÓN DEL ADMIN PARA EL MODELO USUARIO PERSONALIZADO
# -------------------------------------------------------------------

# Heredamos de la clase UserAdmin de Django para no perder ninguna
# de sus funcionalidades (manejo de contraseñas, permisos, etc.)
@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Define la vista de administración para el modelo Usuario personalizado.
    """
    # Campos que se mostrarán en la lista de usuarios
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff')
    
    # Filtros que aparecerán en la barra lateral derecha
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'rol')

    # Campos por los que se puede buscar
    search_fields = ('username', 'first_name', 'last_name', 'email')

    # Esto organiza los campos en el formulario de edición de un usuario.
    # Añadimos nuestra sección "Datos Personales" con los campos nuevos.
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Datos Personales', {'fields': ('rol', 'telefono', 'direccion', 'foto_perfil', 'descripcion')}),
    )

    # Esto añade los campos al formulario de creación de un nuevo usuario.
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Datos Personales', {'fields': ('rol', 'telefono', 'direccion', 'foto_perfil', 'descripcion')}),
    )

# -------------------------------------------------------------------
# CONFIGURACIÓN DEL ADMIN PARA LAS SOLICITUDES DE PROVEEDOR
# -------------------------------------------------------------------
# Tu código original, que está muy bien hecho.
# Lo registramos con el decorador @admin.register para mantener el estilo.

@admin.register(SolicitudProveedor)
class SolicitudProveedorAdmin(admin.ModelAdmin):
    """
    Define la vista de administración para el modelo SolicitudProveedor.
    """
    list_display = ['user', 'nombre_empresa', 'telefono', 'fecha_solicitud', 'aprobado']
    list_filter = ['aprobado']
    search_fields = ['user__username', 'nombre_empresa']
    actions = ['aprobar_solicitud']

    def aprobar_solicitud(self, request, queryset):
        """
        Acción para aprobar las solicitudes de proveedor seleccionadas.
        """
        for solicitud in queryset:
            if not solicitud.aprobado:
                solicitud.aprobado = True
                solicitud.save()
                
                # Actualiza el rol del usuario a 'proveedor' y guarda
                usuario_a_actualizar = solicitud.user
                usuario_a_actualizar.rol = 'proveedor'
                usuario_a_actualizar.save(update_fields=['rol'])

        self.message_user(request, "Las solicitudes seleccionadas fueron aprobadas y los usuarios actualizados a 'proveedor'.")
    
    aprobar_solicitud.short_description = "Aprobar solicitudes de proveedor seleccionadas"