# reports/views.py (CONTENIDO COMPLETO)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required # Puedes usarla si necesitas login_required
from usuarios.decorators import admin_required # Importa el decorador desde la app usuarios

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import json

# Importa TODOS los modelos necesarios usados por esta vista (de tickets y usuarios)
from tickets.models import Evento, Venta, DetalleVenta, Categoria, Opinion 
from usuarios.models import Usuario, SolicitudProveedor


@admin_required # Asegura que solo los admins puedan acceder a este dashboard
def reports_dashboard_view(request): # <-- ¡FUNCIÓN RENOMBRADA!
    # --- Métricas para las tarjetas de acción (copiadas de usuarios/views.py) ---
    solicitudes_pendientes_count = SolicitudProveedor.objects.filter(aprobado=False).count()
    eventos_pendientes_count = Evento.objects.filter(aprobado=False).count()

    # --- KPIs Globales (copiadas de usuarios/views.py) ---
    hace_30_dias = timezone.now() - timedelta(days=30)
    ventas_completas = Venta.objects.filter(estado='completa')
    ventas_recientes = ventas_completas.filter(fecha_compra__gte=hace_30_dias)

    ingresos_brutos_30_dias = ventas_recientes.aggregate(total=Sum('total_bruto'))['total'] or 0
    ganancia_plataforma_30_dias = ventas_recientes.aggregate(total=Sum('comision_plataforma'))['total'] or 0
    ingresos_brutos_totales = ventas_completas.aggregate(total=Sum('total_bruto'))['total'] or 0
    ganancia_plataforma_total = ventas_completas.aggregate(total=Sum('comision_plataforma'))['total'] or 0
    nuevos_usuarios_30_dias = Usuario.objects.filter(date_joined__gte=hace_30_dias).count()
    total_ventas = ventas_completas.count()

    # --- Datos para Gráfico de Ingresos Diarios (copiadas de usuarios/views.py) ---
    ingresos_diarios = (
        ventas_recientes.annotate(dia=TruncDate('fecha_compra')).values('dia').annotate(total=Sum('total_bruto')).order_by('dia')
    )
    labels_ingresos = [i['dia'].strftime('%d %b') for i in ingresos_diarios]
    data_ingresos = [float(i['total']) for i in ingresos_diarios]

    # --- Datos para Gráfico de Tendencias de Usuarios (copiadas de usuarios/views.py) ---
    usuarios_diarios = (
        Usuario.objects.filter(date_joined__gte=hace_30_dias).annotate(dia=TruncDate('date_joined')).values('dia').annotate(cantidad=Count('id')).order_by('dia')
    )
    labels_usuarios = [u['dia'].strftime('%d %b') for u in usuarios_diarios]
    data_usuarios = [u['cantidad'] for u in usuarios_diarios]

    # --- MÉTRICA: DISTRIBUCIÓN DE EVENTOS POR CATEGORÍA (copiada de usuarios/views.py) ---
    eventos_por_categoria = Evento.objects.filter(aprobado=True).values('categoria__nombre').annotate(count=Count('id')).order_by('categoria__nombre')
    labels_categorias = [item['categoria__nombre'] for item in eventos_por_categoria]
    data_categorias = [item['count'] for item in eventos_por_categoria]

    # --- Tablas de Actividad Reciente (copiadas de usuarios/views.py) ---
    ultimas_ventas = ventas_completas.select_related('usuario').order_by('-fecha_compra')[:5]
    ultimos_usuarios = Usuario.objects.order_by('-date_joined')[:5]

    context = {
        'panel_title': 'Panel de Reportes y Análisis', # Nuevo título para este dashboard
        'panel_subtitle': 'Métricas clave sobre el rendimiento de la plataforma.',

        'solicitudes_pendientes_count': solicitudes_pendientes_count,
        'eventos_pendientes_count': eventos_pendientes_count,
        'ingresos_brutos_30_dias': ingresos_brutos_30_dias,
        'ganancia_plataforma_30_dias': ganancia_plataforma_30_dias,
        'ingresos_brutos_totales': ingresos_brutos_totales,
        'ganancia_plataforma_total': ganancia_plataforma_total,
        'nuevos_usuarios_30_dias': nuevos_usuarios_30_dias,
        'total_ventas': total_ventas,

        'labels_ingresos': json.dumps(labels_ingresos),
        'data_ingresos': json.dumps(data_ingresos),
        'labels_usuarios': json.dumps(labels_usuarios),
        'data_usuarios': json.dumps(data_usuarios),
        'labels_categorias': json.dumps(labels_categorias),
        'data_categorias': json.dumps(data_categorias),

        'ultimas_ventas': ultimas_ventas,
        'ultimos_usuarios': ultimos_usuarios,
    }
    return render(request, 'reports/dashboard.html', context)