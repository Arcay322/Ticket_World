// static/js/admin_dashboard.js

document.addEventListener('DOMContentLoaded', function() {

    // Helper function para inicializar gráficos
    function initializeChart(canvasId, type, label, borderColor, backgroundColor, labelsData, chartData, options = {}) {
        const canvasElement = document.getElementById(canvasId);
        if (canvasElement) {
            try {
                // Parsear los datos del dataset del HTML
                const labels = JSON.parse(canvasElement.dataset.labels);
                const data = JSON.parse(canvasElement.dataset.data);

                // Configuración básica del dataset
                const datasetConfig = {
                    label: label,
                    data: data,
                    borderColor: borderColor,
                    backgroundColor: backgroundColor,
                    borderWidth: 1, // Por defecto, se puede sobrescribir
                };

                // Opciones específicas para cada tipo de gráfico o generales
                const defaultOptions = {
                    responsive: true,
                    maintainAspectRatio: false, // Importante para controlar el tamaño con CSS
                    plugins: {
                        legend: {
                            display: true
                        }
                    },
                    scales: { // Sólo para gráficos con ejes (line, bar)
                        y: {
                            beginAtZero: true
                        }
                    }
                };

                // Fusionar opciones predeterminadas con opciones específicas pasadas
                const finalOptions = { ...defaultOptions, ...options };

                // Ajustes específicos para tipos de gráfico
                if (type === 'line') {
                    datasetConfig.tension = 0.3; // Suavidad de la línea
                    datasetConfig.fill = true;   // Rellenar área bajo la línea
                } else if (type === 'pie' || type === 'doughnut') {
                    // Los gráficos de pie no tienen escalas
                    delete finalOptions.scales;
                    // Los colores de fondo se manejan de forma diferente para múltiples segmentos
                    datasetConfig.backgroundColor = [
                        '#007bff', '#28a745', '#ffc107', '#dc3545', // Colores de AdminLTE/Bootstrap
                        '#6c757d', '#17a2b8', '#6610f2', '#fd7e14',
                        '#20c997', '#e83e8c', // Más colores si necesitas
                    ];
                    delete datasetConfig.borderColor; // Sin borde para pie/doughnut por defecto
                    delete datasetConfig.borderWidth;
                } else if (type === 'bar') {
                    finalOptions.scales.y.ticks = { precision: 0 }; // Para valores enteros en barras
                }


                new Chart(canvasElement, {
                    type: type,
                    data: {
                        labels: labels,
                        datasets: [datasetConfig]
                    },
                    options: finalOptions
                });

            } catch (e) {
                console.error(`Error al renderizar el gráfico '${canvasId}':`, e);
                // Opcional: mostrar un mensaje de error en el canvas
                const ctx = canvasElement.getContext('2d');
                ctx.font = '16px Arial';
                ctx.fillStyle = 'red';
                ctx.textAlign = 'center';
                ctx.fillText('Error al cargar el gráfico.', canvasElement.width / 2, canvasElement.height / 2);
            }
        } else {
            console.warn(`Elemento canvas con ID '${canvasId}' no encontrado.`);
        }
    }

    // --- Inicializar Gráfico de Ingresos ---
    initializeChart(
        'ingresosChart',
        'line',
        'Ingresos por Día ($)',
        'rgba(0, 123, 255, 1)', // borderColor
        'rgba(0, 123, 255, 0.1)' // backgroundColor
    );

    // --- Inicializar Gráfico de Nuevos Usuarios ---
    initializeChart(
        'usuariosChart',
        'bar',
        'Nuevos Usuarios por Día',
        'rgba(40, 167, 69, 1)', // borderColor
        'rgba(40, 167, 69, 0.7)' // backgroundColor
    );

    // --- Inicializar Gráfico de Distribución de Eventos por Categoría ---
    // Este era el que faltaba en tu JS!
    initializeChart(
        'categoryPieChart',
        'pie',
        'Distribución de Eventos por Categoría',
        null, // borderColor (no aplica para pie chart con múltiples colores)
        null, // backgroundColor (se define en la función helper para pie charts)
        null, null, // Estos ya no son necesarios aquí gracias a la función helper
        { // Opciones específicas para el gráfico de pie
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: false, // El título ya está en card-header
                }
            },
            // No hay escalas para gráficos de tipo 'pie'
            scales: {} // Vaciar las escalas por defecto para pie chart
        }
    );
});