document.addEventListener('DOMContentLoaded', function () {
    // Configuración común para los gráficos
    const defaultFont = { family: 'Poppins, sans-serif' };

    // Gráfico de Ingresos
    const ingresosChartCtx = document.getElementById('ingresosChart');
    if (ingresosChartCtx) {
        const labelsIngresos = JSON.parse(ingresosChartCtx.dataset.labels);
        const dataIngresos = JSON.parse(ingresosChartCtx.dataset.data);
        new Chart(ingresosChartCtx, {
            type: 'line',
            data: {
                labels: labelsIngresos,
                datasets: [{
                    label: 'Ingresos Brutos',
                    data: dataIngresos,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // Gráfico de Categorías
    const categoriasChartCtx = document.getElementById('categoriasChart');
    if (categoriasChartCtx) {
        const labelsCategorias = JSON.parse(categoriasChartCtx.dataset.labels);
        const dataCategorias = JSON.parse(categoriasChartCtx.dataset.data);
        new Chart(categoriasChartCtx, {
            type: 'doughnut',
            data: {
                labels: labelsCategorias,
                datasets: [{
                    label: 'Nº de Eventos',
                    data: dataCategorias,
                    backgroundColor: ['#0d6efd', '#6c757d', '#198754', '#ffc107', '#dc3545', '#0dcaf0'],
                    borderWidth: 2,
                    hoverOffset: 4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' }}}
        });
    }
});