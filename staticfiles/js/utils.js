// Funciones utilitarias comunes

// Obtener cookie (CSRF)
export function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Debounce: ejecuta fn después de esperar delay ms sin nuevos llamados
export function debounce(fn, delay = 400) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn.apply(this, args), delay);
    };
}

// AJAX request simplificado con manejo de errores y CSRF opcional
export async function ajaxRequest(url, { method = 'GET', data = null, csrf = null, headers = {} } = {}) {
    const opts = {
        method,
        headers: {
            'Content-Type': 'application/json',
            ...headers
        }
    };
    if (csrf) opts.headers['X-CSRFToken'] = csrf;
    if (data) opts.body = JSON.stringify(data);

    const response = await fetch(url, opts);
    if (!response.ok) {
        let errorMsg = 'Error en la petición';
        try {
            const errorData = await response.json();
            errorMsg = errorData.message || errorMsg;
        } catch {}
        throw new Error(errorMsg);
    }
    return response.json();
}

// Mostrar mensaje flash (puedes mejorar esto según tu UI)
export function showFlashMessage(message, type = 'success', duration = 3000) {
    let container = document.querySelector('.messages-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'messages-container';
        document.body.prepend(container);
    }
    const msg = document.createElement('div');
    msg.className = `message-item ${type}`;
    msg.textContent = message;
    container.appendChild(msg);
    setTimeout(() => {
        msg.remove();
        if (!container.hasChildNodes()) container.remove();
    }, duration);
}