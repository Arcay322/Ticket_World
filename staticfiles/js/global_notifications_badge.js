// static/js/global_notifications_badge.js

// Asegúrate de que este script solo se ejecute una vez
if (typeof globalNotificationsBadgeLoaded === 'undefined') {
    var globalNotificationsBadgeLoaded = true;
    console.log('global_notifications_badge.js: script detectado e inicializado.');
    document.addEventListener('DOMContentLoaded', function() {
        console.log('global_notifications_badge.js: DOMContentLoaded disparado.');

        // Verifica si el usuario está autenticado y si la URL para el conteo está disponible
        if (typeof DJANGO_URLS === 'undefined' || !DJANGO_URLS.unreadNotificationsCount || !USER_IS_AUTHENTICATED) {
            console.warn('global_notifications_badge.js: Notificaciones globales no se cargarán: Usuario no autenticado o DJANGO_URLS no disponible.');
            return; 
        }

        const globalUnreadCountBadge = document.getElementById('global-unread-notification-count');
        
        // Función para cargar el conteo de notificaciones no leídas
        window.loadGlobalUnreadNotificationsCount = function() {
            if (!globalUnreadCountBadge) {
                console.log('global_notifications_badge.js: Badge de notificaciones global no encontrado, saltando carga.');
                return;
            }

            fetch(DJANGO_URLS.unreadNotificationsCount)
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 403 || response.status === 401) {
                            console.warn('global_notifications_badge.js: Acceso denegado al conteo de notificaciones. Sesión expirada o usuario no autorizado.');
                            globalUnreadCountBadge.textContent = '';
                            globalUnreadCountBadge.style.display = 'none';
                            return; 
                        }
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    const unreadCount = data.unread_count;
                    if (unreadCount > 0) {
                        globalUnreadCountBadge.textContent = unreadCount;
                        globalUnreadCountBadge.style.display = 'inline-block';
                    } else {
                        globalUnreadCountBadge.textContent = '';
                        globalUnreadCountBadge.style.display = 'none';
                    }
                    console.log(`global_notifications_badge.js: Badge global actualizado a: ${unreadCount}`);
                })
                .catch(error => console.error('global_notifications_badge.js: Error al cargar el conteo global de notificaciones:', error));
        }

        if (globalUnreadCountBadge) {
            loadGlobalUnreadNotificationsCount();
            setInterval(loadGlobalUnreadNotificationsCount, 30000); // Actualiza cada 30 segundos
        }
    });
}