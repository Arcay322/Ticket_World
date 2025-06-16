/* static/js/favorite_logic.js - Lógica centralizada para botones de favorito */
// NOTA: Ahora depende de la función showFlashMessage de messages.js

// ... (todas tus funciones de localStorage se quedan igual, están perfectas) ...
function getFavoriteEventIdsFromLocalStorage() {
    try {
        const favorites = localStorage.getItem('favoriteEventIds');
        return favorites ? JSON.parse(favorites) : [];
    } catch (e) {
        console.error("Error al leer 'favoriteEventIds' de localStorage:", e);
        return [];
    }
}
function saveFavoriteEventIdsToLocalStorage(favoriteIds) {
    try {
        localStorage.setItem('favoriteEventIds', JSON.stringify(favoriteIds));
    } catch (e) {
        console.error("Error al escribir 'favoriteEventIds' en localStorage:", e);
    }
}
function initializeFavoriteButton(buttonElement) {
    const eventoId = buttonElement.dataset.eventoId;
    const heartIcon = buttonElement.querySelector('.feather-heart');
    if (heartIcon && eventoId) {
        const favoriteIds = getFavoriteEventIdsFromLocalStorage();
        if (favoriteIds.includes(eventoId)) {
            heartIcon.classList.add('favorited');
            heartIcon.setAttribute('fill', 'red');
            heartIcon.setAttribute('stroke', 'red');
        } else {
            heartIcon.classList.remove('favorited');
            heartIcon.setAttribute('fill', 'none');
            heartIcon.setAttribute('stroke', 'gray');
        }
    }
}


function handleFavoriteButtonClick(event) {
    event.preventDefault();
    event.stopPropagation();

    const button = this;
    const eventoId = button.dataset.eventoId;
    const url = `/tickets/evento/${eventoId}/toggle-favorito/`;
    const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    button.disabled = true;
    button.style.opacity = 0.7;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
        },
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {
                const errorMessage = errorData.message || `Error del servidor: ${response.status}`;
                // *** CAMBIO AQUÍ ***
                if (typeof showFlashMessage === 'function') {
                    showFlashMessage(errorMessage, 'error');
                }
                throw new Error(errorMessage);
            }).catch(() => {
                // *** CAMBIO AQUÍ ***
                if (typeof showFlashMessage === 'function') {
                    showFlashMessage('Error de conexión o del servidor.', 'error');
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            let currentFavorites = getFavoriteEventIdsFromLocalStorage();
            if (data.is_favorited) {
                if (!currentFavorites.includes(eventoId)) currentFavorites.push(eventoId);
            } else {
                currentFavorites = currentFavorites.filter(id => id !== eventoId);
            }
            saveFavoriteEventIdsToLocalStorage(currentFavorites);

            document.querySelectorAll(`[data-evento-id="${eventoId}"]`).forEach(btn => {
                const iconToUpdate = btn.querySelector('.feather-heart');
                if (iconToUpdate) {
                    iconToUpdate.classList.toggle('favorited', data.is_favorited);
                    iconToUpdate.setAttribute('fill', data.is_favorited ? 'red' : 'none');
                    iconToUpdate.setAttribute('stroke', data.is_favorited ? 'red' : 'gray');
                }
            });

            // *** CAMBIO PRINCIPAL AQUÍ ***
            // Usamos la función correcta: showFlashMessage
            if (data.message && typeof showFlashMessage === 'function') {
                showFlashMessage(data.message, data.is_favorited ? 'success' : 'info');
            }
        } else {
            // *** CAMBIO AQUÍ ***
            if (typeof showFlashMessage === 'function') {
                showFlashMessage(data.message || 'Hubo un error al actualizar tus favoritos.', 'error');
            }
        }
    })
    .catch(error => {
        console.error('Error general en fetch (toggle favorito):', error);
    })
    .finally(() => {
        button.disabled = false;
        button.style.opacity = 1;
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const favoriteButtons = document.querySelectorAll('[data-evento-id]');
    favoriteButtons.forEach(button => {
        initializeFavoriteButton(button);
        button.addEventListener('click', handleFavoriteButtonClick);
    });
});