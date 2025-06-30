// static/js/perfil_notifications.js

// Asegúrate de que este script solo se ejecute una vez
if (typeof perfilNotificationsScriptLoaded === 'undefined') {
    var perfilNotificationsScriptLoaded = true;
    // console.log('perfil_notifications.js: script detectado e inicializado.');
    document.addEventListener('DOMContentLoaded', function() {
        // console.log('perfil_notifications.js: DOMContentLoaded disparado.');

        if (typeof DJANGO_URLS === 'undefined' || !DJANGO_URLS.unreadNotificationsCount || !DJANGO_URLS.markNotificationAsRead || !DJANGO_URLS.perfilBaseUrl) {
            // console.error('perfil_notifications.js: ERROR: DJANGO_URLS o sus URLs de notificación no están definidos. Asegúrate de cargarlo en el HTML.');
            return;
        }
        
        // --- Funciones para la gestión de notificaciones dentro de la Pestaña "Mis Notificaciones" ---
        window.loadUnreadNotificationsCount = function() {
            const profileTabBadge = document.getElementById('unread-notification-count');
            if (!profileTabBadge) { return; }

            fetch(DJANGO_URLS.unreadNotificationsCount)
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 403 || response.status === 401) {
                            // console.warn('perfil_notifications.js: Acceso denegado al conteo de notificaciones. Sesión expirada o usuario no autorizado.');
                            profileTabBadge.textContent = '';
                            profileTabBadge.style.display = 'none';
                        } else {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                    }
                    return response.json();
                })
                .then(data => {
                    const unreadCount = data.unread_count;
                    if (unreadCount > 0) {
                        profileTabBadge.textContent = unreadCount;
                        profileTabBadge.style.display = 'inline-block';
                    } else {
                        profileTabBadge.textContent = '';
                        profileTabBadge.style.display = 'none';
                    }
                    // console.log(`perfil_notifications.js: Badge de pestaña actualizado a: ${unreadCount}`);
                })
                .catch(error => {}); // console.error('perfil_notifications.js: Error al cargar el conteo de notificaciones en el perfil:', error));
        }

        loadUnreadNotificationsCount(); 
        
        const markAllReadBtn = document.getElementById('mark-all-read-btn');
        const perfilContentArea = document.querySelector('.perfil-content-area'); 

        // Función para enviar solicitud para marcar como leída
        function markNotification(notificationId = null, markAll = false) {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const formData = new FormData();

            if (markAll) {
                formData.append('mark_all', 'true');
            } else if (notificationId) {
                formData.append('notification_id', notificationId);
            } else {
                return;
            }
            // console.log(`perfil_notifications.js: Enviando solicitud para marcar notificación(es) como leída. ID: ${notificationId}, Marcar todas: ${markAll}`);
            fetch(DJANGO_URLS.markNotificationAsRead, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formData,
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    // console.log('perfil_notifications.js: Solicitud de marcado como leída EXITOSA.');
                    loadUnreadNotificationsCount(); 
                    if (typeof window.loadGlobalUnreadNotificationsCount === 'function') {
                        window.loadGlobalUnreadNotificationsCount();
                    }

                    if (markAll) {
                        document.querySelectorAll('.notification-item.unread').forEach(item => {
                            item.classList.remove('unread');
                            const markReadButton = item.querySelector('.btn-mark-read');
                            if (markReadButton) markReadButton.style.display = 'none'; 
                        });
                        // console.log('perfil_notifications.js: Todas las notificaciones marcadas como leídas en UI.');
                    } else if (notificationId) {
                        const item = document.querySelector(`.notification-item[data-notification-id="${notificationId}"]`);
                        if (item) {
                            item.classList.remove('unread');
                            const markReadButton = item.querySelector('.btn-mark-read');
                            if (markReadButton) markReadButton.style.display = 'none'; 
                        }
                        // console.log('perfil_notifications.js: Notificación individual marcada como leída en UI.');
                    }
                } else {
                    // console.error('perfil_notifications.js: Error del servidor al marcar notificación:', data.message || 'Error desconocido.');
                }
            })
            .catch(error => {
                // console.error('perfil_notifications.js: Error en la petición AJAX para marcar notificación:', error);
            });
        }

        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', () => {
                // console.log('perfil_notifications.js: Clic en "Marcar todas como leídas".');
                markNotification(null, true); 
            });
        }

        if (perfilContentArea) {
            // console.log('perfil_notifications.js: Adjuntando listener de clic al .perfil-content-area.');
            perfilContentArea.addEventListener('click', function(event) {
                // console.log('perfil_notifications.js: Clic detectado en perfilContentArea. Target:', event.target);

                const clickedMarkReadButton = event.target.closest('.btn-mark-read');
                if (clickedMarkReadButton) {
                    event.preventDefault(); 
                    const notificationId = clickedMarkReadButton.dataset.notificationId;
                    // console.log(`perfil_notifications.js: Clic en 'Marcar como Leída' para ID: ${notificationId}.`);
                    markNotification(notificationId);
                    return; 
                }

                const clickedViewDetailsLink = event.target.closest('a.btn-notification-action');
                if (clickedViewDetailsLink) {
                    event.preventDefault(); // ¡MANTÉN ESTE PREVENT DEFAULT para controlar la navegación!
                    const href = clickedViewDetailsLink.getAttribute('href');
                    
                    let perfilPath = DJANGO_URLS.perfilBaseUrl; 
                    if (!perfilPath.endsWith('/')) { 
                        perfilPath += '/';
                    }

                    // console.log(`perfil_notifications.js: Clic en 'Ver Detalles' Link href: ${href}`);
                    // console.log(`perfil_notifications.js: Ruta de perfil normalizada para comparación: ${perfilPath}`); 

                    if (href && href.startsWith(perfilPath) && href.includes('#')) {
                        const tabName = href.split('#')[1]; 
                        // console.log(`perfil_notifications.js: Es un enlace de pestaña de perfil. Intentando activar pestaña '${tabName}'.`);
                        
                        if (typeof window.openTab === 'function') {
                            const targetTabButton = document.querySelector(`.tab-button[onclick*="'${tabName}'"]`);
                            if (targetTabButton) {
                                // console.log(`perfil_notifications.js: Botón de pestaña '${tabName}' encontrado para activación.`);
                                window.openTab({ currentTarget: targetTabButton }, tabName);
                            } else {
                                // console.error(`perfil_notifications.js: ¡ERROR! Botón de pestaña '${tabName}' NO ENCONTRADO para activación. Fallback a navegación directa.`);
                                window.location.href = href; 
                            }
                        } else {
                            // console.error('perfil_notifications.js: ¡ERROR! window.openTab NO DEFINIDA. Fallback a navegación directa.');
                            window.location.href = href; 
                        }
                    } else {
                        // console.log('perfil_notifications.js: Es una URL externa al perfil. Forzando navegación.');
                        window.location.href = href; 
                    }
                }
            });
        }
    }); // Cierre de DOMContentLoaded
} // Cierre del guard