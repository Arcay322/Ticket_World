// static/js/detalle_evento.js - Ahora solo para el sistema de estrellas y lógica específica del detalle

// La función displayMessage y la lógica de favoritos ha sido movida a static/js/favorite_logic.js
// Asegúrate de que messages.js y favorite_logic.js se carguen antes que este script.


document.addEventListener('DOMContentLoaded', function() {
    try {
        console.log('DEBUG: detalle_evento.js script loaded. (Solo para estrellas)');

        // === CÓDIGO PARA SISTEMA DE ESTRELLAS ===
        const starRatingContainer = document.querySelector('.form-opinion #id_calificacion');

        if (starRatingContainer) {
            const starIconSpans = starRatingContainer.querySelectorAll('.star-rating-option label .star-icon');
            const starLabels = starRatingContainer.querySelectorAll('.star-rating-option label'); 
            let currentRating = 0; // Para almacenar la calificación seleccionada

            // Función para actualizar el estado visual de las estrellas (añade/quita clase 'is-active')
            function updateStarDisplay(ratingToDisplay) {
                console.log(`DEBUG: updateStarDisplay llamada con rating: ${ratingToDisplay}`);
                starIconSpans.forEach((starSpan, index) => {
                    const label = starLabels[index]; // Obtener la etiqueta correspondiente
                    const starValue = parseInt(label.dataset.value); // Obtener el valor del data-value de la label
                    
                    if (starValue <= ratingToDisplay) {
                        starSpan.classList.add('is-active');
                    } else {
                        starSpan.classList.remove('is-active');
                    }
                });
            }

            // Inicializar el estado de las estrellas al cargar si ya hay una seleccionada
            const checkedRadio = starRatingContainer.querySelector('input[type="radio"]:checked');
            if (checkedRadio) {
                currentRating = parseInt(checkedRadio.value);
                updateStarDisplay(currentRating);
            }

            // Eventos para las etiquetas (labels) que son las estrellas clickeables
            starLabels.forEach((label) => { // No necesitamos 'index' aquí
                const starValueFromLabel = parseInt(label.dataset.value);

                label.addEventListener('mouseover', function() {
                    updateStarDisplay(starValueFromLabel); // Ilumina las estrellas hasta la que tiene el ratón
                });

                label.addEventListener('mouseout', function() {
                    updateStarDisplay(currentRating); // Vuelve al estado seleccionado o vacío
                });

                label.addEventListener('click', function() {
                    const clickValue = starValueFromLabel;
                    const correspondingRadio = this.previousElementSibling; // El input radio es el hermano anterior

                    if (correspondingRadio) {
                        correspondingRadio.checked = true; // Marca el radio button como seleccionado
                        currentRating = clickValue; // Actualiza la calificación actual
                        updateStarDisplay(currentRating); // Asegura que el display visual sea el correcto inmediatamente
                    }
                });
            });
        }
        // === FIN DEL CÓDIGO PARA SISTEMA DE ESTRELLAS ===

    } catch (e) {
        console.error('ERROR: Error durante la ejecución de detalle_evento.js:', e);
    }
});