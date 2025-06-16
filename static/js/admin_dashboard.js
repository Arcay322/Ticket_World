// static/js/admin_dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    // Gráfico de Ingresos
    const ingresosCanvas = document.getElementById('ingresosChart');
    if (ingresosCanvas) {
        try {
            const labels = JSON.parse(ingresosCanvas.dataset.labels);
            const data = JSON.parse(ingresosCanvas.dataset.data);
            new Chart(ingresosCanvas, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Ingresos por Día ($)',
                        data: data,
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        borderColor: 'rgba(0, 123, 255, 1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true
                    }]
                }
            });
        } catch (e) { console.error('Error al renderizar gráfico de ingresos:', e); }
    }

    // Gráfico de Nuevos Usuarios
    const usuariosCanvas = document.getElementById('usuariosChart');
    if (usuariosCanvas) {
        try {
            const labels = JSON.parse(usuariosCanvas.dataset.labels);
            const data = JSON.parse(usuariosCanvas.dataset.data);
            new Chart(usuariosCanvas, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Nuevos Usuarios por Día',
                        data: data,
                        backgroundColor: 'rgba(40, 167, 69, 0.7)',
                        borderColor: 'rgba(40, 167, 69, 1)',
                        borderWidth: 1
                    }]
                }
            });
        } catch (e) { console.error('Error al renderizar gráfico de usuarios:', e); }
    }
});