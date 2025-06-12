// static/js/messages.js
document.addEventListener('DOMContentLoaded', function() {
    const messageItems = document.querySelectorAll('.messages-container .message-item');

    messageItems.forEach((message, index) => {
        // Hacemos que cada mensaje aparezca con un pequeño retraso para un efecto escalonado
        setTimeout(() => {
            message.classList.add('show');
        }, 100 * index);

        // Hacemos que el mensaje desaparezca después de 5 segundos
        setTimeout(() => {
            message.classList.remove('show');
            // Opcional: eliminar el elemento del DOM después de la animación
            setTimeout(() => {
                if (message.parentElement) {
                    message.parentElement.removeChild(message);
                }
            }, 600); // 600ms > 500ms de la transición en el CSS
        }, 5000 + (100 * index));
    });
});