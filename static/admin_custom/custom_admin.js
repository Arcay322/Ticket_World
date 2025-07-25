// Ticket_World/static/admin_custom/custom_admin.js

console.log("--> custom_admin.js: Archivo cargado y empezando a ejecutar.");

// ----------------------------------------------------
// PASO 1: CARGA CONDICIONAL DE CHART.JS
// Asegura que Chart.js esté disponible antes de usarlo.
// ----------------------------------------------------
(function() {
    if (typeof Chart === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        script.onload = () => {
            console.log("--> custom_admin.js: Chart.js cargado dinámicamente.");
            initializeAllJazzminCustomScripts();
        };
        script.onerror = (e) => {
            console.error("--> custom_admin.js: ERROR: Falló la carga de Chart.js desde CDN.", e);
        };
        document.head.appendChild(script);
    } else {
        console.log("--> custom_admin.js: Chart.js ya está definido. Procediendo con la inicialización.");
        initializeAllJazzminCustomScripts();
    }
})();


// ----------------------------------------------------
// PASO 2: FUNCIÓN PRINCIPAL DE INICIALIZACIÓN
// Contiene toda la lógica que requiere que el DOM esté listo y Chart.js cargado.
// ----------------------------------------------------
function initializeAllJazzminCustomScripts() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', executeJazzminCustomScripts);
        console.log("--> custom_admin.js: DOM no listo, esperando DOMContentLoaded.");
    } else {
        executeJazzminCustomScripts();
        console.log("--> custom_admin.js: DOM ya listo, ejecutando scripts directamente.");
    }
}

// ----------------------------------------------------
// PASO 3: LÓGICA DE EJECUCIÓN REAL (antes estaba dentro del DOMContentLoaded)
// ----------------------------------------------------
function executeJazzminCustomScripts() {
    console.log("--> custom_admin.js: executeJazzminCustomScripts (DOMContentLoaded o ready) disparado.");

    // --- MANEJO DE FILTROS DE FECHA ---

    const dateFilterForm = document.getElementById('dateFilterForm');
    const fechaInicioInput = document.getElementById('fecha_inicio');
    const fechaFinInput = document.getElementById('fecha_fin');
    const clearDatesBtn = document.getElementById('clearDatesBtn');
    const last30DaysBtn = document.getElementById('last30DaysBtn');
    const currentMonthBtn = document.getElementById('currentMonthBtn');

    // Función para formatear fechas a YYYY-MM-DD
    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };
    
    // Botón "Limpiar Fechas"
    if (clearDatesBtn) {
        clearDatesBtn.addEventListener('click', function() {
            fechaInicioInput.value = '';
            fechaFinInput.value = '';
            dateFilterForm.submit(); // Envía el formulario sin fechas
        });
    }

    // Botón "Últimos 30 días"
    if (last30DaysBtn) {
        last30DaysBtn.addEventListener('click', function() {
            const today = new Date();
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(today.getDate() - 30);

            fechaInicioInput.value = formatDate(thirtyDaysAgo);
            fechaFinInput.value = formatDate(today);
            dateFilterForm.submit();
        });
    }

    // Botón "Mes Actual"
    if (currentMonthBtn) {
        currentMonthBtn.addEventListener('click', function() {
            const today = new Date();
            const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);

            fechaInicioInput.value = formatDate(firstDayOfMonth);
            fechaFinInput.value = formatDate(today);
            dateFilterForm.submit();
        });
    }


    // ----------------------------------------------------
    // LÓGICA DE GRÁFICOS
    // ----------------------------------------------------

    function initializeChart(canvasId, type, label, borderColor, backgroundColor, options = {}) {
        console.log(`--> custom_admin.js: Intentando inicializar gráfico: ${canvasId}`);
        const canvasElement = document.getElementById(canvasId);
        if (canvasElement) {
            try {
                const labels = JSON.parse(canvasElement.dataset.labels);
                const data = JSON.parse(canvasElement.dataset.data);
                console.log(`--> custom_admin.js: Datos para ${canvasId}: Labels -`, labels, "Data -", data);

                if (data.length === 0 || labels.length === 0) {
                    console.warn(`--> custom_admin.js: No hay datos para el gráfico '${canvasId}'.`);
                    const ctx = canvasElement.getContext('2d');
                    ctx.font = '16px Arial';
                    ctx.fillStyle = '#6c757d'; // Color gris
                    ctx.textAlign = 'center';
                    ctx.fillText('No hay datos disponibles.', canvasElement.width / 2, canvasElement.height / 2);
                    return;
                }

                const datasetConfig = {
                    label: label,
                    data: data,
                    borderColor: borderColor,
                    backgroundColor: backgroundColor,
                    borderWidth: 1,
                };

                const defaultOptions = {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: true }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                };

                const finalOptions = { ...defaultOptions, ...options };

                if (type === 'line') {
                    datasetConfig.tension = 0.3;
                    datasetConfig.fill = true;
                } else if (type === 'pie' || type === 'doughnut') {
                    delete finalOptions.scales;
                    datasetConfig.backgroundColor = [
                        '#007bff', '#28a745', '#ffc107', '#dc3545',
                        '#6c757d', '#17a2b8', '#6610f2', '#fd7e14',
                        '#20c997', '#e83e8c', 
                        '#adb5bd', '#6f42c1', '#20c997', '#e83e8c' 
                    ];
                    delete datasetConfig.borderColor;
                    delete datasetConfig.borderWidth;
                } else if (type === 'bar') {
                    finalOptions.scales.y.ticks = { precision: 0 };
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
                console.error(`--> custom_admin.js: ERROR al renderizar el gráfico '${canvasId}':`, e);
                const ctx = canvasElement.getContext('2d');
                ctx.font = '16px Arial';
                ctx.fillStyle = 'red';
                ctx.textAlign = 'center';
                ctx.fillText('Error al cargar el gráfico.', canvasElement.width / 2, canvasElement.height / 2);
            }
        } else {
            console.warn(`--> custom_admin.js: WARNING: Elemento canvas con ID '${canvasId}' no encontrado.`);
        }
    }

    // --- Llamadas a inicializar Gráficos ---
    initializeChart('ingresosChart', 'line', 'Ingresos Brutos (Rango)', 'rgba(0, 123, 255, 1)', 'rgba(0, 123, 255, 0.1)');
    initializeChart('usuariosChart', 'bar', 'Nuevos Usuarios (Rango)', 'rgba(40, 167, 69, 1)', 'rgba(40, 167, 69, 0.7)');
    initializeChart('eventosCategoriaChart', 'pie', 'Eventos por Categoría (Cantidad)', null, null, {
        plugins: { legend: { position: 'top' }, title: { display: false } }, scales: {}
    });
    initializeChart('ventasCategoriaChart', 'pie', 'Ventas por Categoría (Ingresos)', null, null, {
        plugins: { legend: { position: 'top' }, title: { display: false } }, scales: {}
    });


    // ----------------------------------------------------
    // LÓGICA DE BADGES Y SIDEBAR (TU CÓDIGO ORIGINAL)
    // ----------------------------------------------------

    function setupNavLinkWithBadge(linkElement, countFetchUrl, badgeColorClass) {
        if (linkElement) {
            console.log(`--> custom_admin.js: setupNavLinkWithBadge: Procesando enlace con texto: '${linkElement.textContent.trim()}'.`);
            linkElement.style.display = 'flex';
            linkElement.style.alignItems = 'center';
            linkElement.style.justifyContent = 'space-between';
            linkElement.style.gap = '8px';

            fetch(countFetchUrl)
                .then(response => {
                    if (!response.ok) {
                        console.error(`--> custom_admin.js: ERROR FETCH: Respuesta de red no OK para ${countFetchUrl}. Estado: ${response.status}`);
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    const count = data.count;
                    console.log(`--> custom_admin.js: Conteo recibido para '${linkElement.textContent.trim()}': ${count}`);
                    let badge = linkElement.querySelector(`.badge.${badgeColorClass}`);

                    if (count > 0) {
                        if (!badge) {
                            badge = document.createElement('span');
                            badge.className = `badge ${badgeColorClass} ml-auto badge-pill`;
                            linkElement.appendChild(badge);
                            console.log(`--> custom_admin.js: Badge CREADO para '${linkElement.textContent.trim()}' con conteo ${count}.`);
                        } else {
                            console.log(`--> custom_admin.js: Badge ACTUALIZADO para '${linkElement.textContent.trim()}' con conteo ${count}.`);
                        }
                        badge.textContent = count;
                        badge.style.display = '';
                    } else {
                        if (badge) {
                            badge.style.display = 'none';
                            console.log(`--> custom_admin.js: Badge OCULTADO para '${linkElement.textContent.trim()}' (conteo 0).`);
                        } else {
                            console.log(`--> custom_admin.js: No hay badge para ocultar para '${linkElement.textContent.trim()}' (conteo 0).`);
                        }
                    }
                })
                .catch(error => {
                    console.error(`--> custom_admin.js: ERROR en fetch o promesa para '${countFetchUrl}':`, error);
                    const badge = linkElement.querySelector(`.badge.${badgeColorClass}`);
                    if (badge) badge.style.display = 'none';
                });
        } else {
            console.warn(`--> custom_admin.js: WARNING: Enlace no encontrado para el selector/elemento. Esto es inesperado.`);
        }
    }

    function updateSidebarActiveState() {
        console.log("--> custom_admin.js: Ejecutando actualización de estado activo del sidebar.");
        const currentPathAndQuery = window.location.pathname + window.location.search;

        const pendingEventsLink = document.querySelector('a[href*="/admin/tickets/evento/?aprobado"]');
        const pendingSupplierRequestsLink = document.querySelector('a[href*="/admin/usuarios/solicitudproveedor/?aprobado"]');

        const standardEventsLink = document.querySelector('a[href="/admin/tickets/evento/"]');
        const standardSupplierRequestsLink = document.querySelector('a[href="/admin/usuarios/solicitudproveedor/"]');

        const toggleActiveClass = (linkElement, isActive) => {
            if (linkElement) {
                const parentLi = linkElement.closest('li.nav-item');
                if (isActive) {
                    linkElement.classList.add('active');
                    if (parentLi) parentLi.classList.add('active');
                    console.log(`--> custom_admin.js: Activado: '${linkElement.textContent.trim()}'`);
                } else {
                    linkElement.classList.remove('active');
                    if (parentLi) parentLi.classList.remove('active');
                    console.log(`--> custom_admin.js: Desactivado: '${linkElement.textContent.trim()}'`);
                }
            }
        };

        if (pendingEventsLink && currentPathAndQuery.includes(pendingEventsLink.getAttribute('href'))) {
            toggleActiveClass(standardEventsLink, false);
            toggleActiveClass(pendingEventsLink, true);
        } else if (standardEventsLink && currentPathAndQuery.includes(standardEventsLink.getAttribute('href')) && !currentPathAndQuery.includes('?')) {
            toggleActiveClass(standardEventsLink, true);
        }

        if (pendingSupplierRequestsLink && currentPathAndQuery.includes(pendingSupplierRequestsLink.getAttribute('href'))) {
            toggleActiveClass(standardSupplierRequestsLink, false);
            toggleActiveClass(pendingSupplierRequestsLink, true);
        } else if (standardSupplierRequestsLink && currentPathAndQuery.includes(standardSupplierRequestsLink.getAttribute('href')) && !currentPathAndQuery.includes('?')) {
            toggleActiveClass(standardSupplierRequestsLink, true);
        }
    }


    // --- EJECUTAR LAS LLAMADAS DE BADGES Y ESTADO ACTIVO ---
    setTimeout(function() {
        console.log("--> custom_admin.js: Iniciando actualizaciones de badges y estado activo después de 100ms.");

        const allBadgesUpdate = function() {
            setupNavLinkWithBadge(document.querySelector('a[href="/admin/tickets/adminnotification/"]'), '/tickets/admin-notifications-count/', 'badge-danger');
            setupNavLinkWithBadge(document.querySelector('a[href*="/admin/tickets/evento/?aprobado"]'), '/tickets/admin-pending-events-count/', 'badge-warning');
            setupNavLinkWithBadge(document.querySelector('a[href*="/admin/usuarios/solicitudproveedor/?aprobado"]'), '/tickets/admin-pending-supplier-requests-count/', 'badge-info');
            setupNavLinkWithBadge(document.querySelector('.nav-link[href="/admin/tickets/adminnotification/"]'), '/tickets/admin-notifications-count/', 'badge-danger');
        };
        allBadgesUpdate();

        updateSidebarActiveState();

    }, 100);

    setInterval(function() {
        console.log("--> custom_admin.js: Iniciando actualización periódica de badges y estado activo.");
        setTimeout(function() {
            allBadgesUpdate();
            updateSidebarActiveState();
        }, 100);
    }, 10000);

}