// static/js/favorite_logic.js (VERSIÓN FINAL Y COMPLETA CON SINCRONIZACIÓN AUTOMÁTICA)

/**
 * Actualiza el atributo 'fill' de todos los iconos de corazón en la página
 * basándose en el estado de favorito inicial del evento.
 * Esta función es crucial para cuando el DOM se carga inicialmente o se actualiza vía AJAX.
 */
function updateAllFavoriteHearts() {
    console.log("DEBUG: updateAllFavoriteHearts: Evaluando todos los corazones en el DOM.");
    
    // Selecciona todos los botones de favorito en la página.
    // Esto incluye los de la página de detalle (.btn-favorito) y los de las tarjetas (.btn-favorito-card).
    document.querySelectorAll('.btn-favorito, .btn-favorito-card').forEach(button => {
        const iconToUpdate = button.querySelector('.feather-heart');
        if (iconToUpdate) {
            // Verifica el estado inicial de favorito del evento a través de las clases en el SVG.
            // Si el SVG tiene la clase 'favorited' al cargar, se pinta de rojo.
            // Esto asume que tu template Django ya pone la clase 'favorited' o el 'fill' correcto.
            const isFavoritedInitially = iconToUpdate.classList.contains('favorited') || iconToUpdate.getAttribute('fill') === 'red';
            iconToUpdate.setAttribute('fill', isFavoritedInitially ? 'red' : 'none');
            // Asegúrate de que la clase 'favorited' también esté sincronizada si la usas para CSS
            iconToUpdate.classList.toggle('favorited', isFavoritedInitially);
            console.log(`DEBUG: Corazón para evento ${button.dataset.eventoId} inicializado a: ${isFavoritedInitially ? 'favorito' : 'no favorito'}`);
        }
    });
}

/**
 * Maneja la lógica de alternar el estado de favorito de un evento mediante una petición AJAX.
 * @param {HTMLElement} button - El botón de favorito clickeado (con data-evento-id).
 * @param {Event} event - El evento de click.
 */
function handleFavoriteToggle(button, event) {
    event.preventDefault(); 
    event.stopPropagation(); 

    const eventoId = button.dataset.eventoId;
    const url = `/tickets/evento/${eventoId}/toggle-favorito/`; 
    
    const csrftokenElement = document.querySelector('meta[name="csrf-token"]');
    const csrftoken = csrftokenElement ? csrftokenElement.getAttribute('content') : '';

    if (!csrftoken) {
        console.error("Error: CSRF token no encontrado.");
        if (typeof showFlashMessage === 'function') {
            showFlashMessage('Error de seguridad: Token CSRF no encontrado.', 'error');
        }
        return; 
    }

    button.disabled = true; 

    fetch(url, {
        method: 'POST', 
        headers: {
            'X-Requested-With': 'XMLHttpRequest', 
            'X-CSRFToken': csrftoken,            
            'Content-Type': 'application/json'   
        },
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
            }).catch(() => {
                throw new Error(`HTTP error! status: ${response.status} (No JSON response)`);
            });
        }
        return response.json(); 
    })
    .then(data => {
        if (data.status === 'success') {
            // --- LÓGICA DE ACTUALIZACIÓN VISUAL PARA TODOS LOS CORAZONES DEL MISMO EVENTO ---
            // Selecciona *todos* los botones de favorito en la página actual
            // relacionados con este evento (por su `data-evento-id`).
            document.querySelectorAll(`
                .btn-favorito[data-evento-id="${eventoId}"],
                .btn-favorito-card[data-evento-id="${eventoId}"]
            `).forEach(btnElement => {
                const iconToUpdate = btnElement.querySelector('.feather-heart');
                if (iconToUpdate) {
                    iconToUpdate.setAttribute('fill', data.is_favorited ? 'red' : 'none');
                    iconToUpdate.classList.toggle('favorited', data.is_favorited); // Sincroniza la clase también
                }
            });
            // --- FIN LÓGICA DE ACTUALIZACIÓN VISUAL ---

            if (typeof showFlashMessage === 'function') {
                showFlashMessage(data.message, data.is_favorited ? 'success' : 'info');
            }

        } else {
            if (typeof showFlashMessage === 'function') {
                showFlashMessage(data.message || 'Error del servidor.', 'error');
            } else {
                console.error('Error del servidor:', data.message);
            }
        }
    })
    .catch(error => {
        console.error('Error en la operación de favorito:', error);
        if (typeof showFlashMessage === 'function') {
            showFlashMessage('No se pudo completar la acción. Inténtalo de nuevo.', 'error');
        }
    })
    .finally(() => {
        button.disabled = false; 
    });
}

// === DELEGACIÓN DE EVENTOS GLOBAL PARA TODOS LOS BOTONES DE FAVORITO ===
// Este listener se adjunta UNA SOLA VEZ al 'document'.
// Captura clics en cualquier parte y usa `closest()` para identificar si el clic
// ocurrió dentro de un botón de favorito. Esto funciona para elementos ya existentes
// y para aquellos que se añaden dinámicamente al DOM.
document.addEventListener('click', function(event) {
    const favoriteButton = event.target.closest('.btn-favorito, .btn-favorito-card');
    if (favoriteButton) {
        handleFavoriteToggle(favoriteButton, event);
    }
});

// === INICIALIZACIÓN Y SINCRONIZACIÓN AL CARGAR/ACTUALIZAR EL DOM ===
// 1. Al cargar el DOM inicial (cuando la página se carga por primera vez).
document.addEventListener('DOMContentLoaded', updateAllFavoriteHearts);

// 2. Cuando el contenido de una sección se actualiza vía AJAX (ej. en inicio.js).
// El 'domUpdated' es un evento personalizado que `inicio.js` disparará.
document.addEventListener('domUpdated', updateAllFavoriteHearts);