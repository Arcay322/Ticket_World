// static/js/messages.js

/**
 * Muestra un mensaje flash dinámico en la pantalla.
 * @param {string} message - El texto del mensaje a mostrar.
 * @param {string} type - El tipo de mensaje ('success', 'error', 'info', 'warning').
 */
function showFlashMessage(message, type = 'success') {
    let container = document.querySelector('.messages-container');
    if (!container) {
        container = document.createElement('ul');
        container.className = 'messages-container';
        document.body.appendChild(container);
    }

    const messageItem = document.createElement('li');
    messageItem.className = `message-item ${type}`;
    messageItem.textContent = message;
    container.appendChild(messageItem);

    setTimeout(() => {
        messageItem.classList.add('show');
    }, 50);

    const displayDuration = 5000;
    const fadeOutDuration = 500;

    setTimeout(() => {
        messageItem.classList.remove('show');
        setTimeout(() => {
            messageItem.remove();
        }, fadeOutDuration);
    }, displayDuration);
}


// Lógica para manejar los mensajes que ya vienen renderizados por Django
document.addEventListener('DOMContentLoaded', function() {
    if (window.djangoMessagesProcessed) return;
    window.djangoMessagesProcessed = true;
    
    const initialMessages = document.querySelectorAll('.messages-container .message-item');
    
    if (initialMessages.length > 0) {
        initialMessages.forEach((messageItem, index) => {
            setTimeout(() => {
                messageItem.classList.add('show');
                const displayDuration = 5000;
                const fadeOutDuration = 500;
                setTimeout(() => {
                    messageItem.classList.remove('show');
                    setTimeout(() => {
                        messageItem.remove();
                    }, fadeOutDuration);
                }, displayDuration + (index * 200));
            }, 100 + (index * 150));
        });
    }
});