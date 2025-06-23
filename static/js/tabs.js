// static/js/tabs.js

document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const eventListContainer = document.getElementById('seccion-eventos'); // Contenedor de la lista de eventos
    
    // Función para obtener los parámetros actuales de la URL, excepto 'page', 'tab' y 'scroll_to'
    function getCurrentUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const paramsToKeep = new URLSearchParams();
        for (const [key, value] of urlParams.entries()) {
            // Excluimos 'page', 'tab' y 'scroll_to' para reconstruir la URL base de la pestaña
            if (key !== 'page' && key !== 'tab' && key !== 'scroll_to') {
                paramsToKeep.append(key, value);
            }
        }
        return paramsToKeep;
    }

    // Función para cargar el contenido de una pestaña
    function loadTabContent(tabType, page = 1) {
        if (!eventListContainer) {
            console.warn("Element with ID 'seccion-eventos' not found. Cannot load tab content.");
            return;
        }

        const currentParams = getCurrentUrlParams();
        currentParams.set('tab', tabType); // Añade el parámetro de la pestaña actual
        currentParams.set('page', page); // Añade el parámetro de la página actual (normalmente 1 al cambiar de pestaña)

        const url = `/usuarios/inicio/?${currentParams.toString()}`; // Construye la URL completa para la petición AJAX

        // Muestra un indicador de carga (atenuando el contenido)
        eventListContainer.style.opacity = '0.5';

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest' // Encabezado para que Django detecte la petición AJAX
            }
        })
        .then(response => {
            if (!response.ok) {
                // Si la respuesta no es OK (ej. 404, 500), lanza un error
                throw new Error(`HTTP error! status: ${response.status} from ${response.url}`);
            }
            return response.text(); // Espera HTML como respuesta
        })
        .then(html => {
            eventListContainer.innerHTML = html; // Reemplaza el contenido del contenedor con el nuevo HTML
            eventListContainer.style.opacity = '1'; // Restaura la opacidad
            
            // Actualiza la URL en el navegador sin recargar la página (para que sea compartible y el historial funcione)
            const newUrl = new URL(window.location.href);
            newUrl.search = currentParams.toString();
            window.history.pushState({ path: newUrl.href }, '', newUrl.href);

            // IMPORTANTE: Vuelve a adjuntar los event listeners de paginación si se han perdido.
            // Esto asume que `pagination.js` expone una función `attachPaginationListeners` global.
            if (typeof attachPaginationListeners === 'function') { // Verifica si la función existe
                attachPaginationListeners();
            }

            // IMPORTANTE: RE-INICIALIZA LOS CONTADORES PARA LOS NUEVOS ELEMENTOS DE LA PESTAÑA
            if (typeof initializeCountdowns === 'function') { // Verifica si la función existe
                initializeCountdowns();
            }

            // Opcional: Volver a desplazar a la sección de eventos si se cambia de pestaña desde arriba.
            // if (typeof scrollToSeccionEventos === 'function') {
            //     scrollToSeccionEventos();
            // }

        })
        .catch(error => {
            console.error('Error al cargar el contenido de la pestaña AJAX:', error);
            eventListContainer.style.opacity = '1'; // Restaura la opacidad incluso con error
            // Opcional: Mostrar un mensaje de error amigable al usuario en el DOM.
        });
    }

    // Event listeners para los botones de las pestañas
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remueve la clase 'active' de todos los botones de pestaña
            tabButtons.forEach(btn => btn.classList.remove('active'));
            // Añade la clase 'active' al botón de la pestaña clickeada
            this.classList.add('active');
            
            const tabType = this.dataset.tabType; // Obtiene el tipo de pestaña del atributo data-tab-type
            loadTabContent(tabType); // Carga el contenido de la nueva pestaña (siempre a la página 1)
        });
    });

    // Lógica para que la pestaña activa refleje el estado de la URL al cargar la página.
    // Esto asegura que si recargas la página con ?tab=nuevos, la pestaña "Nuevos Eventos" se vea activa.
    const initialUrlParams = new URLSearchParams(window.location.search);
    const initialTab = initialUrlParams.get('tab') || 'proximos'; // Pestaña inicial de la URL o por defecto 'proximos'

    // Activa visualmente el botón de la pestaña inicial
    tabButtons.forEach(button => {
        if (button.dataset.tabType === initialTab) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });

    // NOTA: No necesitamos llamar a `loadTabContent(initialTab)` aquí, porque Django ya renderiza
    // el contenido inicial para la pestaña predeterminada (`proximos`) o la que viene en la URL.
    // El JS solo se encarga de cambiar el contenido a partir del primer clic de pestaña.
});