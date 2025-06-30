// static/js/countdown.js

// Función principal para inicializar y actualizar todos los contadores
function initializeCountdowns() {
    console.log("DEBUG: Initializing countdowns...");
    const countdownElements = document.querySelectorAll('.event-countdown');

    countdownElements.forEach(element => {
        const eventDateStr = element.dataset.eventDate;
        if (!eventDateStr) {
            console.warn("Countdown element missing 'data-event-date' attribute:", element);
            return;
        }

        const eventDate = new Date(eventDateStr);
        // Almacenar la fecha de fin y el ID del intervalo para poder limpiarlo
        element._eventEndDate = eventDate;
        element._countdownIntervalId = null; // Para almacenar el ID del intervalo

        updateCountdown(element); // Actualiza inmediatamente al cargar

        // Limpia cualquier intervalo anterior para este elemento (importante para AJAX)
        if (element._countdownIntervalId) {
            clearInterval(element._countdownIntervalId);
        }

        // Inicia el contador cada segundo
        element._countdownIntervalId = setInterval(() => {
            updateCountdown(element);
        }, 1000);
    });
}

// Función para calcular y mostrar el tiempo restante para un elemento específico
function updateCountdown(element) {
    const now = new Date().getTime();
    const distance = element._eventEndDate.getTime() - now;

    const daysSpan = element.querySelector('.countdown-days');
    const hoursSpan = element.querySelector('.countdown-hours');
    const minutesSpan = element.querySelector('.countdown-minutes');
    const secondsSpan = element.querySelector('.countdown-seconds');

    if (distance < 0) {
        // Evento ha terminado
        element.innerHTML = '¡Evento Finalizado!';
        element.classList.add('event-ended');
        if (element._countdownIntervalId) {
            clearInterval(element._countdownIntervalId); // Detiene el contador
        }
        return;
    } else if (distance < 3600000) { // Menos de 1 hora
        element.innerHTML = '¡En curso!'; // O "Evento en las próximas horas"
        element.classList.add('event-ended'); // Puedes usar otra clase para "casi empieza"
        if (element._countdownIntervalId) {
            clearInterval(element._countdownIntervalId); // Detiene el contador
        }
        return;
    }

    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    if (daysSpan) daysSpan.textContent = days;
    if (hoursSpan) hoursSpan.textContent = hours;
    if (minutesSpan) minutesSpan.textContent = minutes;
    if (secondsSpan) secondsSpan.textContent = seconds;

    // Puedes ocultar días, horas, etc. si son 0 y no quieres mostrarlos
    // Ej: if (days === 0 && daysSpan) daysSpan.parentElement.style.display = 'none';
}

// Llama a la función de inicialización cuando el DOM esté completamente cargado.

// *** INTEGRACIÓN CON AJAX (IMPORTANTE) ***
// Cuando el contenido del DOM cambia debido a AJAX (paginación o cambio de pestaña),
// necesitamos volver a inicializar los contadores para los nuevos elementos.
// Asegúrate de que las funciones de pagination.js y tabs.js llamen a initializeCountdowns()
// después de actualizar el innerHTML.

// Para pagination.js y tabs.js:
// Después de `eventListContainer.innerHTML = html;`
// Añade: `initializeCountdowns();`
// (Ya lo haremos en los siguientes pasos de integración)