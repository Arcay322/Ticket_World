# reports/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from usuarios.decorators import admin_required
from django.db.models import Count, Sum, F, ExpressionWrapper, fields
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, datetime
import json
import csv # Para exportar datos
from django.http import HttpResponse # Para devolver archivos CSV

# Importa TODOS los modelos necesarios
from tickets.models import Evento, Venta, DetalleVenta, Categoria
from usuarios.models import Usuario, SolicitudProveedor

# --- NUEVO: Vistas para Exportación a CSV ---

@admin_required
def export_ventas_csv(request):
    # Reutiliza la lógica de filtrado de la vista principal
    fecha_inicio_str = request.GET.get('fecha_inicio', (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    fecha_fin_str = request.GET.get('fecha_fin', timezone.now().strftime('%Y-%m-%d'))
    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time(), tzinfo=timezone.get_current_timezone())

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_ventas_{fecha_inicio}_a_{fecha_fin}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID Venta', 'Usuario', 'Email Usuario', 'Monto Bruto', 'Comision Plataforma', 'Ganancia Proveedor', 'Fecha Compra'])

    ventas = Venta.objects.filter(
        estado='completa',
        fecha_compra__date__gte=fecha_inicio,
        fecha_compra__lte=fecha_fin_dt
    ).select_related('usuario').order_by('-fecha_compra')

    for venta in ventas:
        writer.writerow([
            venta.id,
            venta.usuario.username,
            venta.usuario.email,
            venta.total_bruto,
            venta.comision_plataforma,
            venta.ganancia_proveedor,
            venta.fecha_compra.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response

@admin_required
def export_proveedores_csv(request):
    # Lógica de filtrado
    fecha_inicio_str = request.GET.get('fecha_inicio', (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    fecha_fin_str = request.GET.get('fecha_fin', timezone.now().strftime('%Y-%m-%d'))
    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time(), tzinfo=timezone.get_current_timezone())
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="rendimiento_proveedores_{fecha_inicio}_a_{fecha_fin}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Proveedor', 'Ingresos Generados', 'Boletos Vendidos', 'Eventos Activos'])
    
    top_proveedores = (
        Venta.objects.filter(
            estado='completa',
            fecha_compra__date__gte=fecha_inicio,
            fecha_compra__lte=fecha_fin_dt
        )
        .values('detalles__boleto__evento__creado_por__username')
        .annotate(
            ingresos_generados=Sum('total_bruto'),
            boletos_vendidos=Sum('detalles__cantidad')
        )
        .order_by('-ingresos_generados')
    )

    for proveedor in top_proveedores:
        username = proveedor['detalles__boleto__evento__creado_por__username']
        eventos_activos = Evento.objects.filter(creado_por__username=username, aprobado=True).count()
        writer.writerow([
            username,
            proveedor['ingresos_generados'],
            proveedor['boletos_vendidos'],
            eventos_activos
        ])
    return response

# --- VISTA PRINCIPAL DEL DASHBOARD ---

@admin_required
def reports_dashboard_view(request):
    # --- Manejo de Filtros de Fecha ---
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    try:
        if fecha_inicio_str:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        else:
            fecha_inicio = (timezone.now() - timedelta(days=30)).date()

        if fecha_fin_str:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time(), tzinfo=timezone.get_current_timezone())
        else:
            fecha_fin = timezone.now().date()
            fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time(), tzinfo=timezone.get_current_timezone())
    except ValueError:
        fecha_inicio = (timezone.now() - timedelta(days=30)).date()
        fecha_fin = timezone.now().date()
        fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time(), tzinfo=timezone.get_current_timezone())
        print("ADVERTENCIA: Formato de fecha inválido. Usando rango por defecto.")
        
    print(f"Dashboard filtrado para rango: {fecha_inicio} a {fecha_fin}")

    # --- KPIs filtrados por el rango de fechas ---
    ventas_completas_en_rango = Venta.objects.filter(
        estado='completa',
        fecha_compra__date__gte=fecha_inicio,
        fecha_compra__lte=fecha_fin_dt
    )
    
    ingresos_brutos_rango = ventas_completas_en_rango.aggregate(total=Sum('total_bruto'))['total'] or 0
    ganancia_plataforma_rango = ventas_completas_en_rango.aggregate(total=Sum('comision_plataforma'))['total'] or 0
    total_ventas_rango = ventas_completas_en_rango.count()
    nuevos_usuarios_rango = Usuario.objects.filter(
        date_joined__date__gte=fecha_inicio,
        date_joined__lte=fecha_fin_dt
    ).count()

    # --- NUEVO: Lógica para Alertas y Metas Visuales en KPIs ---
    num_dias_rango = max(1, (fecha_fin - fecha_inicio).days) # Evitar división por cero
    
    # Meta: Ganancia de $50 diarios en promedio
    ganancia_promedio_diaria = ganancia_plataforma_rango / num_dias_rango
    if ganancia_promedio_diaria >= 50:
        ganancia_status_color = 'success' # Verde (excelente)
    elif ganancia_promedio_diaria >= 20:
        ganancia_status_color = 'warning' # Amarillo (regular)
    else:
        ganancia_status_color = 'danger' # Rojo (bajo)

    # Meta: 2 nuevos usuarios diarios en promedio
    usuarios_promedio_diarios = nuevos_usuarios_rango / num_dias_rango
    if usuarios_promedio_diarios >= 2:
        usuarios_status_color = 'success'
    elif usuarios_promedio_diarios >= 1:
        usuarios_status_color = 'warning'
    else:
        usuarios_status_color = 'danger'


    # --- KPIs Totales Históricos (no cambian) ---
    ingresos_brutos_totales = Venta.objects.filter(estado='completa').aggregate(total=Sum('total_bruto'))['total'] or 0
    ganancia_plataforma_total = Venta.objects.filter(estado='completa').aggregate(total=Sum('comision_plataforma'))['total'] or 0
    total_usuarios_registrados = Usuario.objects.count()
    total_proveedores_activos = Usuario.objects.filter(rol='proveedor').count()
    total_eventos_aprobados = Evento.objects.filter(aprobado=True).count()
    
    # ... (código de gráficos de ingresos y usuarios sin cambios) ...
    ingresos_diarios = (
        ventas_completas_en_rango
        .annotate(dia=TruncDate('fecha_compra'))
        .values('dia')
        .annotate(total=Sum('total_bruto'))
        .order_by('dia')
    )
    date_labels = [(fecha_inicio + timedelta(days=x)).strftime('%d %b') for x in range((fecha_fin - fecha_inicio).days + 1)]
    ingresos_data_map = {i['dia'].strftime('%d %b'): float(i['total']) for i in ingresos_diarios}
    data_ingresos = [ingresos_data_map.get(label, 0) for label in date_labels]
    labels_ingresos = date_labels

    usuarios_diarios_rango = (
        Usuario.objects.filter(
            date_joined__date__gte=fecha_inicio,
            date_joined__lte=fecha_fin_dt
        )
        .annotate(dia=TruncDate('date_joined'))
        .values('dia')
        .annotate(cantidad=Count('id'))
        .order_by('dia')
    )
    usuarios_data_map = {u['dia'].strftime('%d %b'): u['cantidad'] for u in usuarios_diarios_rango}
    data_usuarios = [usuarios_data_map.get(label, 0) for label in date_labels]
    labels_usuarios = date_labels
    
    # ... (código de gráficos de categorías sin cambios) ...
    eventos_por_categoria_count = Evento.objects.filter(aprobado=True).values('categoria__nombre').annotate(count=Count('id')).order_by('categoria__nombre')
    labels_eventos_categoria = [item['categoria__nombre'] for item in eventos_por_categoria_count]
    data_eventos_categoria = [item['count'] for item in eventos_por_categoria_count]
    
    ventas_por_categoria_ingresos = (
        ventas_completas_en_rango
        .values('detalles__boleto__evento__categoria__nombre')
        .annotate(total_ingresos=Sum('total_bruto'))
        .order_by('detalles__boleto__evento__categoria__nombre')
    ).exclude(total_ingresos__isnull=True)

    labels_ventas_categoria = [item['detalles__boleto__evento__categoria__nombre'] for item in ventas_por_categoria_ingresos]
    data_ventas_categoria = [float(item['total_ingresos']) for item in ventas_por_categoria_ingresos]

    # --- Tablas de Actividad Reciente ---
    ultimas_ventas = ventas_completas_en_rango.select_related('usuario').order_by('-fecha_compra')[:10]
    ultimos_usuarios = Usuario.objects.filter(
        date_joined__date__gte=fecha_inicio,
        date_joined__lte=fecha_fin_dt
    ).order_by('-date_joined')[:5]

    top_eventos_vendidos_data = (
        ventas_completas_en_rango
        .values(
            'detalles__boleto__evento__id', 
            'detalles__boleto__evento__nombre',
            'detalles__boleto__evento__categoria__nombre',
        )
        .annotate(
            ingresos_totales_evento=Sum('total_bruto'),
            boletos_vendidos_evento=Sum('detalles__cantidad')
        )
        .order_by('-ingresos_totales_evento')
        [:5]
    )
    
    # --- NUEVO: Desglose de Ventas por Tipo de Boleto ---
    ventas_por_tipo_boleto = (
        DetalleVenta.objects.filter(
            venta__in=ventas_completas_en_rango
        )
        .values('boleto__tipo')
        .annotate(
            ingresos_totales=Sum(F('cantidad') * F('precio_unitario')),
            cantidad_vendida=Sum('cantidad')
        )
        .order_by('-ingresos_totales')
    )

    # --- NUEVO: Rendimiento de Proveedores ---
    top_proveedores = (
        ventas_completas_en_rango
        .values(
            'detalles__boleto__evento__creado_por__username'
        )
        .annotate(
            ingresos_generados=Sum('total_bruto'),
            boletos_vendidos=Sum('detalles__cantidad')
        )
        .order_by('-ingresos_generados')[:5]
    )

    context = {
        'panel_title': 'Panel de Reportes y Análisis', 
        'panel_subtitle': 'Métricas clave sobre el rendimiento de la plataforma.',

        'fecha_inicio_seleccionada': fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_fin_seleccionada': fecha_fin.strftime('%Y-%m-%d'),

        # KPIs filtrados
        'ingresos_brutos_rango': ingresos_brutos_rango,
        'ganancia_plataforma_rango': ganancia_plataforma_rango,
        'total_ventas_rango': total_ventas_rango,
        'nuevos_usuarios_rango': nuevos_usuarios_rango,

        # --- NUEVO: Estados de color para KPIs ---
        'ganancia_status_color': ganancia_status_color,
        'usuarios_status_color': usuarios_status_color,

        # KPIs Totales
        'ingresos_brutos_totales': ingresos_brutos_totales,
        'ganancia_plataforma_total': ganancia_plataforma_total,
        'total_usuarios_registrados': total_usuarios_registrados,
        'total_proveedores_activos': total_proveedores_activos,
        'total_eventos_aprobados': total_eventos_aprobados,

        # Datos para gráficos (convertidos a JSON)
        'labels_ingresos': json.dumps(labels_ingresos),
        'data_ingresos': json.dumps(data_ingresos),
        'labels_usuarios': json.dumps(labels_usuarios),
        'data_usuarios': json.dumps(data_usuarios),
        'labels_eventos_categoria': json.dumps(labels_eventos_categoria), 
        'data_eventos_categoria': json.dumps(data_eventos_categoria),
        'labels_ventas_categoria': json.dumps(labels_ventas_categoria),
        'data_ventas_categoria': json.dumps(data_ventas_categoria),

        # Datos para tablas
        'ultimas_ventas': ultimas_ventas,
        'ultimos_usuarios': ultimos_usuarios,
        'top_eventos_vendidos': top_eventos_vendidos_data,
        
        # --- NUEVO: Datos para nuevas tablas ---
        'ventas_por_tipo_boleto': ventas_por_tipo_boleto,
        'top_proveedores': top_proveedores,
    }
    return render(request, 'reports/dashboard.html', context)