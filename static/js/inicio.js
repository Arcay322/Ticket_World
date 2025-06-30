// static/js/inicio.js

document.addEventListener('DOMContentLoaded', function() {

    // --- Funciones auxiliares ---

    // Llama a la función del contador (asegúrate de que countdown.js se carga antes)
    console.log("DOM Cargado. Llamando a initializeCountdowns por primera vez.");
    if (typeof initializeCountdowns === 'function') {
        initializeCountdowns();
    } else {
        console.error("Error: La función initializeCountdowns no existe.");
    }

    /**
     * Realiza un scroll suave a una posición Y específica.
     * @param {number} endY - La posición Y final a la que se debe desplazar.
     * @param {number} duration - La duración de la animación en milisegundos.
     */
    function customSmoothScroll(endY, duration) {
        const startY = window.scrollY;
        const distanceY = endY - startY;
        let startTime = null;

        function animation(currentTime) {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const progress = Math.min(timeElapsed / duration, 1);
            const ease = 0.5 * (1 - Math.cos(Math.PI * progress)); // Función de easing para suavizado

            window.scrollTo(0, startY + distanceY * ease);

            if (timeElapsed < duration) {
                requestAnimationFrame(animation);
            }
        }
        requestAnimationFrame(animation);
    }

    /**
     * Maneja las peticiones AJAX para actualizar la sección de eventos.
     * @param {string} url - La URL para la petición AJAX.
     */
    function handleAjaxRequest(url) {
        const seccionEventos = document.getElementById('seccion-eventos');
        if (!seccionEventos) {
            console.error("#seccion-eventos no encontrado para la petición AJAX.");
            return;
        }

        seccionEventos.style.opacity = '0.5'; // Indicar estado de carga

        fetch(url, { 
            headers: { 
                'X-Requested-With': 'XMLHttpRequest' // Para que Django lo detecte como AJAX
            } 
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            seccionEventos.innerHTML = html; // Reemplaza el contenido de la sección
            seccionEventos.style.opacity = '1'; // Quita indicación de carga

            // Vuelve a inicializar los contadores para los nuevos eventos cargados
            if (typeof initializeCountdowns === 'function') {
                initializeCountdowns();
            }

            // Realiza el scroll después de que el nuevo contenido está en el DOM
            const offset = 120; // Ajusta según la altura de tu encabezado fijo
            const y = seccionEventos.getBoundingClientRect().top + window.scrollY - offset;
            customSmoothScroll(y, 100); 
            
            // Actualiza la URL del navegador sin recargar la página (para mantener historial/compartir)
            history.pushState(null, '', url);

            // --- NUEVO: Disparar evento personalizado después de actualizar el DOM ---
            // Esto le dice a otros scripts (como favorite_logic.js) que el contenido ha cambiado.
            document.dispatchEvent(new CustomEvent('domUpdated'));
            // --- FIN NUEVO ---

        })
        .catch(error => {
            console.error('Error durante la petición AJAX:', error);
            seccionEventos.style.opacity = '1'; // Asegura que la opacidad se restaure en caso de error
        });
    }

    // --- Lógica principal ---

    // 1. Scroll al cargar la página (para búsquedas y filtros de categoría)
    const urlParams = new URLSearchParams(window.location.search);
    const scrollToParam = urlParams.get('scroll_to'); 

    if (scrollToParam === 'events') {
        const targetElement = document.getElementById('seccion-eventos'); 
        if (targetElement) {
            setTimeout(() => {
                const offset = 120;
                const y = targetElement.getBoundingClientRect().top + window.scrollY - offset;
                customSmoothScroll(y, 100); 
            }, 50);
        }
    }

    // 2. Manejo de paginación con AJAX
    const seccionEventos = document.getElementById('seccion-eventos');
    if (seccionEventos) { 
        seccionEventos.addEventListener('click', function(event) {
            const paginationLink = event.target.closest('.pagination a');
            if (paginationLink) {
                event.preventDefault(); 
                const url = new URL(paginationLink.href);
                url.searchParams.set('scroll_to', 'events'); 
                handleAjaxRequest(url.toString());
            }
        });
    } else {
        console.warn("Elemento con ID 'seccion-eventos' no encontrado. La paginación AJAX no funcionará.");
    }

    // 3. Manejo de cambio de pestañas con AJAX
    const tabNavigation = document.querySelector('.tabs-container'); 
    if (tabNavigation) {
        tabNavigation.addEventListener('click', function(event) {
            const tabButton = event.target.closest('.tab-button');
            if (tabButton) {
                event.preventDefault(); 
                const tabType = tabButton.dataset.tabType; 

                document.querySelectorAll('.tab-button').forEach(btn => {
                    btn.classList.remove('active');
                });
                tabButton.classList.add('active');

                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('tab', tabType);
                currentUrl.searchParams.delete('q'); 
                currentUrl.searchParams.delete('categoria'); 
                currentUrl.searchParams.delete('page'); 
                currentUrl.searchParams.set('scroll_to', 'events'); 

                handleAjaxRequest(currentUrl.toString());
            }
        });

        // Lógica para establecer la pestaña activa al cargar la página
        const initialTab = urlParams.get('tab');
        const defaultTabButton = document.querySelector('.tab-button[data-tab-type="proximos"]');

        if (initialTab) {
            const activeTabButton = document.querySelector(`.tab-button[data-tab-type="${initialTab}"]`);
            if (activeTabButton) {
                document.querySelectorAll('.tab-button').forEach(btn => {
                    btn.classList.remove('active');
                });
                activeTabButton.classList.add('active');
            } else if (defaultTabButton) {
                defaultTabButton.classList.add('active');
            }
        } else {
            if (defaultTabButton) {
                defaultTabButton.classList.add('active');
            }
        }
    } else {
        console.warn("Elemento .tabs-container no encontrado. La navegación por pestañas no funcionará.");
    }
});