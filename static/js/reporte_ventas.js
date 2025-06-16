function inicializarGraficoVentasDiarias() {
    const canvas = document.getElementById('ventasPorDiaChart');
    if (!canvas) return;

    try {
        const labels = JSON.parse(canvas.dataset.labels);
        const data = JSON.parse(canvas.dataset.data);

        new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Ingresos por Día ($)',
                    data: data,
                    backgroundColor: 'rgba(0, 172, 193, 0.2)',
                    borderColor: 'rgba(0, 172, 193, 1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                }]
            }
        });
    } catch (e) {
        console.error("Error al inicializar el gráfico de ventas diarias:", e);
    }
}

function inicializarGraficoBoletosPorTipo() {
    const canvas = document.getElementById('boletosPorTipoChart');
    if (!canvas) return;

    try {
        const labels = JSON.parse(canvas.dataset.labels);
        const data = JSON.parse(canvas.dataset.data);

        new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Cantidad de Boletos',
                    data: data,
                    backgroundColor: [
                        'rgba(0, 172, 193, 0.8)',   // Turquesa
                        'rgba(255, 152, 0, 0.8)',   // Naranja
                        'rgba(76, 175, 80, 0.8)',    // Verde
                        'rgba(244, 67, 54, 0.8)',    // Rojo
                        'rgba(153, 102, 255, 0.8)',  // Púrpura
                        'rgba(54, 162, 235, 0.8)',   // Azul
                        'rgba(255, 206, 86, 0.8)',   // Amarillo
                        'rgba(96, 125, 139, 0.8)'    // Gris Azulado
                    ],
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            }
        });
    } catch (e) {
        console.error("Error al inicializar el gráfico de tipo de boletos:", e);
    }
}


document.addEventListener('DOMContentLoaded', function() {
    inicializarGraficoVentasDiarias();
    inicializarGraficoBoletosPorTipo();
});