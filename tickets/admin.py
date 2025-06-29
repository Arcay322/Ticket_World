# tickets/admin.py

from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
# Importa los modelos necesarios
from .models import Categoria, Evento, Boleto, MetodoPago, Venta, DetalleVenta, Opinion, AdminNotification
# Importa lo necesario para enviar notificaciones al usuario
from usuarios.views import create_web_notification 
from django.contrib.auth import get_user_model 


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'creado_en')
    search_fields = ('nombre',)

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)

class BoletoInline(admin.TabularInline):
    model = Boleto
    extra = 1

# --- ¡INICIO DE LA REORDENACIÓN! ---

# Mover DetalleVentaInline AQUI, antes de VentaAdmin
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('boleto', 'cantidad', 'precio_unitario')


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_compra', 'estado', 'total_bruto', 'comision_plataforma')
    # --- ¡CAMBIO AQUÍ! AÑADIR 'usuario' al list_filter ---
    list_filter = ('estado', 'fecha_compra', 'usuario') 
    search_fields = ('id', 'usuario__username')
    readonly_fields = ('fecha_compra', 'total_bruto', 'comision_plataforma', 'ganancia_proveedor')
    inlines = [DetalleVentaInline]

# --- ¡FIN DE LA REORDENACIÓN! ---


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'creado_por', 'fecha', 'categoria', 'aprobado', 'esta_activo', 'acciones_en_fila')
    list_filter = ('aprobado', 'esta_activo', 'categoria', 'creado_por')
    search_fields = ('nombre', 'lugar', 'creado_por__username')
    ordering = ('-fecha',)
    inlines = [BoletoInline] # BoletoInline también debe estar definida antes de EventoAdmin
    actions = ['aprobar_eventos', 'rechazar_eventos', 'publicar_eventos', 'ocultar_eventos']

    @admin.action(description='Aprobar eventos seleccionados')
    def aprobar_eventos(self, request, queryset):
        updated_count = queryset.update(aprobado=True) # Actualiza el campo 'aprobado' en la DB
        
        print(f'DEBUG_ADMIN_ACTION: Iniciando bulk approve. {updated_count} eventos actualizados en DB.') 
        
        for evento in queryset:
            if evento.creado_por:
                print(f'DEBUG_ADMIN_ACTION: Llamando create_web_notification para {evento.creado_por.username} (Evento: {evento.nombre}).')
                create_web_notification(
                    evento.creado_por, 
                    'evento_aprobado', 
                    f'¡Tu evento "{evento.nombre}" ha sido aprobado!', 
                    link=reverse('tickets:detalle_evento', args=[evento.id])
                )
            else:
                print(f'DEBUG_ADMIN_ACTION: Evento "{evento.nombre}" no tiene creador. No se envía notificación a usuario.')

        self.message_user(request, f'{updated_count} eventos aprobados correctamente.')

    @admin.action(description='Rechazar eventos seleccionados')
    def rechazar_eventos(self, request, queryset):
        for evento in queryset:
            evento.aprobado = False 
            if evento.creado_por:
                create_web_notification(
                    evento.creado_por,
                    'evento_rechazado',
                    f'Tu evento "{evento.nombre}" ha sido rechazado.',
                    link=reverse('tickets:panel_proveedor')
                )
        self.message_user(request, f'{queryset.count()} eventos rechazados y marcados como "No Aprobado".', level='warning')
        
    @admin.action(description='Activar visibilidad (Publicar)')
    def publicar_eventos(self, request, queryset):
        queryset.update(esta_activo=True)

    @admin.action(description='Desactivar visibilidad (Ocultar)')
    def ocultar_eventos(self, request, queryset):
        queryset.update(esta_activo=False)
        
    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        
        custom_urls = [
            path('<path:object_id>/aprobar/', self.admin_site.admin_view(self.aprobar_evento_view), name='%s_%s_aprobar' % info),
            path('<path:object_id>/rechazar/', self.admin_site.admin_view(self.rechazar_evento_view), name='%s_%s_rechazar' % info),
        ]
        return custom_urls + urls

    def aprobar_evento_view(self, request, object_id):
        evento = self.get_object(request, object_id)
        evento.aprobado = True
        evento.save() 
        self.message_user(request, f'DEBUG_INLINE_APPROVE: Evento "{evento.nombre}" aprobado via botón individual.')
        print(f'DEBUG_INLINE_APPROVE: Evento "{evento.nombre}" aprobado via botón individual. Enviando notif.') 

        if evento.creado_por:
            create_web_notification(
                evento.creado_por,
                'evento_aprobado',
                f'¡Tu evento "{evento.nombre}" ha sido aprobado!',
                link=reverse('tickets:detalle_evento', args=[evento.id])
            )
        else:
            print(f'DEBUG_INLINE_APPROVE: Evento "{evento.nombre}" no tiene creador. No se envía notificación a usuario.')

        return HttpResponseRedirect(reverse('admin:tickets_evento_changelist'))

    def rechazar_evento_view(self, request, object_id):
        evento = self.get_object(request, object_id)
        evento_nombre = evento.nombre
        
        if evento.creado_por:
            create_web_notification(
                evento.creado_por, 'evento_rechazado', f'Tu evento "{evento_nombre}" ha sido rechazado.',
                link=reverse('tickets:panel_proveedor')
            )
        evento.delete() 
        self.message_user(request, f'El evento "{evento_nombre}" ha sido rechazado y eliminado.')
        return HttpResponseRedirect(reverse('admin:tickets_evento_changelist'))
        
    def acciones_en_fila(self, obj):
        if not obj.aprobado:
            url_aprobar = reverse('admin:tickets_evento_aprobar', args=[obj.pk])
            url_rechazar = reverse('admin:tickets_evento_rechazar', args=[obj.pk])
            
            return format_html(
                '<a href="{}" class="button btn-success btn-sm" style="margin-right: 5px;">Aprobar</a>'
                '<a href="{}" class="button btn-danger btn-sm">Rechazar</a>',
                url_aprobar,
                url_rechazar
            )
        return "Acción realizada"
        
    acciones_en_fila.short_description = 'Acciones Rápidas'
    
@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = ('evento', 'usuario', 'calificacion', 'estado')
    # --- ¡CAMBIO AQUÍ! AÑADIR 'usuario' al list_filter ---
    list_filter = ('estado', 'calificacion', 'evento', 'usuario')
    search_fields = ('comentario', 'usuario__username', 'evento__nombre')
    actions = ['aprobar_opiniones', 'rechazar_opiniones']

    @admin.action(description='Aprobar opiniones seleccionadas')
    def aprobar_opiniones(self, request, queryset):
        queryset.update(estado='aprobada')

    @admin.action(description='Rechazar opiniones seleccionadas')
    def rechazar_opiniones(self, request, queryset):
        queryset.update(estado='rechazada')

# --- REGISTRO DEL NUEVO MODELO DE NOTIFICACIÓN DEL ADMIN ---
@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'recipient', 'type', 'read', 'created_at', 'link')
    list_filter = ('type', 'read', 'created_at')
    search_fields = ('message', 'recipient__username')
    readonly_fields = ('created_at', 'recipient', 'message', 'type', 'link')
    actions = ['mark_as_read', 'mark_as_unread']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(recipient=request.user)
        return qs.none() 


    @admin.action(description='Marcar seleccionadas como leídas')
    def mark_as_read(self, request, queryset):
        queryset = queryset.filter(recipient=request.user)
        updated = queryset.update(read=True)
        self.message_user(request, f"{updated} notificaciones marcadas como leídas.")

    @admin.action(description='Marcar seleccionadas como no leídas')
    def mark_as_unread(self, request, queryset):
        queryset = queryset.filter(recipient=request.user)
        queryset = queryset.filter(recipient=request.user)
        updated = queryset.update(read=False)
        self.message_user(request, f"{updated} notificaciones marcadas como no leídas.")