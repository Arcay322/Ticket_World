# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, SolicitudProveedor, UserNotification # <-- ¡Importa UserNotification!
from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(UserAdmin):
    model = Usuario
    list_display = ('username', 'email', 'rol', 'is_active', 'date_joined')
    list_filter = ('rol', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'telefono', 'direccion', 'foto_perfil')}),
    )
    actions = ['activar_usuarios', 'desactivar_usuarios', 'hacer_proveedor']

    @admin.action(description='Marcar usuarios seleccionados como Activos')
    def activar_usuarios(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Marcar usuarios seleccionados como Inactivos')
    def desactivar_usuarios(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description='Convertir usuarios seleccionados en Proveedores')
    def hacer_proveedor(self, request, queryset):
        queryset.update(rol='proveedor')

admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(SolicitudProveedor)
admin.site.register(UserNotification) # <-- ¡Registra tu UserNotification aquí!