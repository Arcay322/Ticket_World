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

class SolicitudProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'email', 'telefono', 'nombre_empresa', 'aprobado', 'fecha_solicitud', 'user')
    list_filter = ('aprobado', 'fecha_solicitud')
    search_fields = ('nombres', 'apellidos', 'email', 'nombre_empresa', 'user__username')
    list_select_related = ('user',)
    raw_id_fields = ('user',)
    list_per_page = 25

class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'message', 'read', 'created_at')
    list_filter = ('notification_type', 'read', 'created_at')
    search_fields = ('message', 'recipient__username')
    list_select_related = ('recipient',)
    raw_id_fields = ('recipient',)
    list_per_page = 25

admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(SolicitudProveedor, SolicitudProveedorAdmin)
admin.site.register(UserNotification, UserNotificationAdmin) # <-- ¡Registra tu UserNotification aquí!