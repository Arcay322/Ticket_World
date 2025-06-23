// static/js/inicio.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('DEBUG: inicio.js script loaded.');

    try {
        const urlParams = new URLSearchParams(window.location.search);
        console.log('DEBUG: URL Search Params (todos):', urlParams.toString());

        const qParam = urlParams.get('q');
        console.log('DEBUG: Parámetro de búsqueda (q):', qParam);

        const scrollToEventsExplicitlyRequested = urlParams.has('scroll_to') && urlParams.get('scroll_to') === 'events';
        console.log('DEBUG: Condición "scroll_to=events" explícita cumplida:', scrollToEventsExplicitlyRequested);

        if (scrollToEventsExplicitlyRequested || qParam) {
            // El contenedor principal de la sección de eventos (que tiene el ID)
            const sectionContainer = document.getElementById('seccion-eventos');

            if (sectionContainer) {
                // Buscamos el H2 con la clase .section-title dentro de ese contenedor
                const targetTitleElement = sectionContainer.querySelector('.section-title');

                console.log('DEBUG: Elemento de título encontrado:', targetTitleElement ? 'Sí' : 'No');

                if (targetTitleElement) {
                    // Usar requestAnimationFrame para un desplazamiento más suave
                    requestAnimationFrame(() => {
                        setTimeout(() => {
                            // Calcula la posición vertical del elemento respecto al viewport
                            const elementRect = targetTitleElement.getBoundingClientRect();
                            const offsetTop = elementRect.top + window.scrollY;

                            // Define un offset extra (por ejemplo, para dejar un pequeño margen superior)
                            // Ajusta este valor si tienes un header fijo que lo tapa.
                            const customOffset = 120; // 80px por ejemplo, ajusta según necesidad
                            
                            window.scrollTo({
                                top: offsetTop - customOffset,
                                behavior: 'smooth'
                            });
                            console.log('DEBUG: Desplazado a la posición del título.');
                        }, 100); // Pequeño retraso para dar tiempo al renderizado
                    });
                } else {
                    console.warn('DEBUG: Advertencia: Elemento de título ".section-title" no encontrado dentro de #seccion-eventos.');
                }
            } else {
                console.warn('DEBUG: Advertencia: Elemento #seccion-eventos no encontrado para el desplazamiento.');
            }
        } else {
            console.log('DEBUG: No se cumplen las condiciones para el desplazamiento automático.');
        }
    } catch (e) {
        console.error('DEBUG: Error durante la ejecución de inicio.js:', e);
    }
});