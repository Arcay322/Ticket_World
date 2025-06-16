// static/js/inicio.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('DEBUG: inicio.js script loaded.'); // Confirmación de que el script se carga

    try {
        const urlParams = new URLSearchParams(window.location.search);
        console.log('DEBUG: URL Search Params (todos):', urlParams.toString()); // Registra todos los parámetros

        const qParam = urlParams.get('q'); // Obtiene el valor del parámetro 'q' (consulta de búsqueda)
        console.log('DEBUG: Parámetro de búsqueda (q):', qParam); // Registra el valor de 'q'

        const scrollToEventsExplicitlyRequested = urlParams.has('scroll_to') && urlParams.get('scroll_to') === 'events';
        console.log('DEBUG: Condición "scroll_to=events" explícita cumplida:', scrollToEventsExplicitlyRequested);

        // La condición para desplazar ahora es:
        // 1. Si 'scroll_to=events' está explícitamente en la URL (como en el caso de categorías).
        // O
        // 2. Si el parámetro 'q' (búsqueda) está presente en la URL.
        // Esto asegura el scroll después de una búsqueda incluso si el '&scroll_to=events' falta.
        if (scrollToEventsExplicitlyRequested || qParam) { 
            const targetElement = document.getElementById('seccion-eventos');
            console.log('DEBUG: Elemento de destino #seccion-eventos encontrado:', targetElement ? 'Sí' : 'No');

            if (targetElement) {
                // Usar requestAnimationFrame para un desplazamiento más suave después del renderizado del DOM
                // y un pequeño retraso para el reflow de la página.
                requestAnimationFrame(() => {
                    setTimeout(() => {
                        targetElement.scrollIntoView({ behavior: 'smooth' });
                        console.log('DEBUG: Desplazado a #seccion-eventos.');
                    }, 100); // Pequeño retraso para dar tiempo al renderizado de la página
                });
            } else {
                console.warn('DEBUG: Advertencia: Elemento #seccion-eventos no encontrado para el desplazamiento.');
            }
        } else {
            console.log('DEBUG: No se cumplen las condiciones para el desplazamiento automático.');
        }
    } catch (e) {
        console.error('DEBUG: Error durante la ejecución de inicio.js:', e); // Captura errores generales del script
    }
});