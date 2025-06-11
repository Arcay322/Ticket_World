document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todos los elementos de mensaje
    const messageItems = document.querySelectorAll('.messages-list .message-item');

    messageItems.forEach((item, index) => {
        // Pequeño retraso para la animación de entrada secuencial
        setTimeout(() => {
            item.classList.add('show'); // Añadir clase para deslizar hacia abajo

            // Establecer un temporizador para que el mensaje desaparezca
            const displayDuration = 4000; // 4 segundos visible
            const fadeOutDuration = 500; // 0.5 segundos para la transición de salida

            setTimeout(() => {
                item.classList.remove('show'); // Quitar la clase 'show'
                item.classList.add('hide'); // Añadir clase para la animación de desaparición

                // Eliminar el mensaje del DOM después de que la animación de salida termine
                setTimeout(() => {
                    item.remove();
                }, fadeOutDuration);

            }, displayDuration + (index * 200)); // Añadir un pequeño desfase para mensajes múltiples
        }, 100 + (index * 100)); // Pequeño retraso inicial para cada mensaje
    });
});
