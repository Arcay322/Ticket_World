// static/js/panel_proveedor.js (VERSIÓN FINAL)

// Función para inicializar el gráfico de ingresos mensuales
function inicializarGraficoIngresos() {
    const canvas = document.getElementById('ingresosMesChart');
    if (!canvas) return;

    try {
        const labels = JSON.parse(canvas.dataset.labels);
        const data = JSON.parse(canvas.dataset.data);

        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Ingresos por Mes ($)',
                    data: data,
                    backgroundColor: 'rgba(0, 172, 193, 0.7)',
                    borderColor: 'rgba(0, 172, 193, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: { y: { beginAtZero: true } },
                responsive: true,
                plugins: { legend: { position: 'top' } }
            }
        });
    } catch (e) {
        console.error('Error al procesar los datos para el gráfico de ingresos:', e);
    }
}

// Función para inicializar el gráfico de Top 5 Eventos
function inicializarGraficoTopEventos() {
    const canvas = document.getElementById('topEventosChart');
    if (!canvas) return;

    try {
        const labels = JSON.parse(canvas.dataset.labels);
        const data = JSON.parse(canvas.dataset.data);

        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Ingresos por Evento ($)',
                    data: data,
                    backgroundColor: [
                        'rgba(0, 172, 193, 0.7)', 'rgba(255, 152, 0, 0.7)',
                        'rgba(76, 175, 80, 0.7)', 'rgba(244, 67, 54, 0.7)',
                        'rgba(153, 102, 255, 0.7)'
                    ]
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: { legend: { display: false } }
            }
        });
    } catch (e) {
        console.error('Error al procesar los datos para el gráfico de top eventos:', e);
    }
}


// --- LÓGICA DE PAGINACIÓN AJAX (CORREGIDA Y MÁS ROBUSTA) ---
function inicializarPaginacionAjax() {
    const container = document.getElementById('gestion-eventos-container');
    if (!container) {
        console.error('El contenedor para paginación AJAX #gestion-eventos-container no fue encontrado.');
        return;
    }

    container.addEventListener('click', function(event) {
        const link = event.target.closest('a.page-link');

        if (!link || link.parentElement.classList.contains('disabled')) {
            return;
        }

        event.preventDefault(); // Prevenimos la recarga de la página

        const url = link.href;
        const pageQuery = url.split('?')[1];

        container.style.opacity = '0.5';

        fetch(`/tickets/panel-proveedor/filtrar-eventos/?${pageQuery}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('La respuesta del servidor no fue exitosa.');
                }
                return response.text();
            })
            .then(html => {
                container.innerHTML = html;
                container.style.opacity = '1';

                // ===============================================
                //       ¡AQUÍ ESTÁ LA LÍNEA MÁGICA!
                // ===============================================
                // Buscamos el título de la tabla que acabamos de cargar
                const tableTitle = container.querySelector('h3');
                
                if (tableTitle) {
                    // Hacemos que la página se desplace suavemente hasta ese título
                    tableTitle.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            })
            .catch(error => {
                console.error('Error durante la paginación AJAX:', error);
                container.style.opacity = '1';
            });
    });
}

// --- INICIALIZADOR PRINCIPAL ---
document.addEventListener('DOMContentLoaded', function() {
    inicializarGraficoIngresos();
    inicializarGraficoTopEventos();
    inicializarPaginacionAjax();
});