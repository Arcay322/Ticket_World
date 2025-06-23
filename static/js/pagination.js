document.addEventListener('DOMContentLoaded', function() {
    const eventListContainer = document.getElementById('seccion-eventos');

    if (!eventListContainer) {
        console.warn("Element with ID 'seccion-eventos' not found. AJAX pagination will not be active.");
        return;
    }

    function handlePaginationClick(event) {
        const paginationLink = event.target.closest('.pagination a');

        if (paginationLink) {
            event.preventDefault();

            const url = paginationLink.href;
            eventListContainer.style.opacity = '0.5';

            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status} from ${response.url}`);
                }
                return response.text();
            })
            .then(html => {
                eventListContainer.innerHTML = html;
                eventListContainer.style.opacity = '1';

                // --- INICIO DE LA LÓGICA DE SCROLL MANUAL ---
                const scrollMargin = 100; // <-- ¡Este es tu margen manual en píxeles! Ajústalo a tu gusto.
                const yOffset = -scrollMargin;
                const y = eventListContainer.getBoundingClientRect().top + window.scrollY + yOffset;
                window.scrollTo({top: y, behavior: 'smooth'});
                // --- FIN DE LA LÓGICA DE SCROLL MANUAL ---

                if (typeof initializeCountdowns === 'function') {
                    initializeCountdowns();
                }
            })
            .catch(error => {
                console.error('Error al cargar la paginación AJAX:', error);
                eventListContainer.style.opacity = '1';
            });
        }
    }
    
    eventListContainer.addEventListener('click', handlePaginationClick);
});