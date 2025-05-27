from django.contrib import admin
from django.contrib import admin
from .models import SolicitudProveedor

@admin.register(SolicitudProveedor)
class SolicitudProveedorAdmin(admin.ModelAdmin):
    list_display = ['user', 'nombre_empresa', 'telefono', 'fecha_solicitud', 'aprobado']
    list_filter = ['aprobado']
    search_fields = ['user__username', 'nombre_empresa']

    # Aquí puedes agregar acciones para aprobar solicitudes
    actions = ['aprobar_solicitud']

    def aprobar_solicitud(self, request, queryset):
        for solicitud in queryset:
            if not solicitud.aprobado:
                solicitud.aprobado = True
                solicitud.save()
                # Convertir al usuario en proveedor
                solicitud.user.rol = 'proveedor'
                solicitud.user.save()
        self.message_user(request, "Las solicitudes seleccionadas fueron aprobadas.")
    aprobar_solicitud.short_description = "Aprobar solicitud"
