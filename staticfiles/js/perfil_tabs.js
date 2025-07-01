// static/js/perfil_tabs.js

// Añade una variable global para asegurar que el script solo se ejecute una vez
if (typeof perfilTabsScriptLoaded === 'undefined') {
    var perfilTabsScriptLoaded = true;
    // console.log('perfil_tabs.js: script detectado e inicializado.');
    document.addEventListener('DOMContentLoaded', function() {
        // console.log('perfil_tabs.js: DOMContentLoaded disparado.');

        // --- Lógica para Pestañas (Tabs) ---
        // Esta función ahora está diseñada para ser llamada tanto por clic directo
        // como programáticamente (ej. desde perfil_notifications.js)
        window.openTab = function(evt, tabName) {
            // console.log(`openTab: *** Llama a openTab para '${tabName}' ***`);
            // console.log('openTab: Evento currentTarget:', evt ? evt.currentTarget : 'No event target');

            // 1. Ocultar todos los contenidos de pestaña y quitar 'active'
            const tabContents = document.getElementsByClassName("tab-content");
            for (let i = 0; i < tabContents.length; i++) {
                tabContents[i].style.display = "none";
                tabContents[i].classList.remove('active');
            }
            // console.log('openTab: Contenidos de pestaña ocultados.');

            // 2. Quitar 'active' de todos los botones de pestaña
            const tabButtons = document.getElementsByClassName("tab-button");
            for (let i = 0; i < tabButtons.length; i++) {
                tabButtons[i].classList.remove("active");
            }
            // console.log('openTab: Clases active de botones removidas.');

            // 3. Mostrar el contenido de la pestaña deseada y añadir 'active'
            const targetContent = document.getElementById(tabName);
            if (targetContent) {
                targetContent.style.display = "block";
                targetContent.classList.add('active');
                // console.log(`openTab: Contenido #${tabName} mostrado y activado.`);
            } else {
                // console.error(`openTab: ¡ERROR! Contenido de pestaña '${tabName}' NO ENCONTRADO.`);
            }

            // 4. Activar el botón de la pestaña correspondiente
            let activatedButton = null;
            if (evt && evt.currentTarget) {
                activatedButton = evt.currentTarget;
            } else {
                activatedButton = document.querySelector(`.tab-button[onclick*="'${tabName}'"]`);
                if (!activatedButton) {
                     // console.warn(`openTab: Botón de pestaña para '${tabName}' no encontrado por onclick. Intenta otra búsqueda.`);
                }
            }
            
            if (activatedButton) {
                activatedButton.classList.add("active");
                // console.log(`openTab: Botón para '${tabName}' activado.`);
            } else {
                // console.error(`openTab: ¡ERROR! No se pudo encontrar el botón de pestaña para activar: '${tabName}'`);
            }

            // 5. Actualiza el hash de la URL (solo si es diferente para evitar entradas duplicadas en el historial)
            if (window.location.hash.substring(1) !== tabName) {
                history.pushState(null, null, `#${tabName}`);
                // console.log(`openTab: Hash de URL actualizado a: #${tabName}`);
            }
            
            // 6. Si la pestaña de notificaciones se activa, recargar el conteo
            if (tabName === 'mis-notificaciones' && typeof window.loadUnreadNotificationsCount === 'function') {
                window.loadUnreadNotificationsCount();
                // console.log('openTab: loadUnreadNotificationsCount llamado.');
            }
            // console.log('openTab: --- Fin de openTab ---');
        }

        // --- Lógica de Activación Inicial de Pestañas ---
        const urlHash = window.location.hash.substring(1); 
        let initialTabFound = false;

        if (urlHash) {
            const initialTabButton = document.querySelector(`.tab-button[onclick*="'${urlHash}'"]`);
            if (initialTabButton) {
                window.openTab({ currentTarget: initialTabButton }, urlHash);
                initialTabFound = true;
            } else {
                // console.warn(`perfil_tabs.js: Hash "${urlHash}" en URL pero botón de pestaña no encontrado. Activando primera pestaña.`);
            }
        }

        if (!initialTabFound) {
            const firstTabButton = document.querySelector('.perfil-tabs .tab-button');
            if (firstTabButton) {
                const firstTabNameMatch = firstTabButton.getAttribute('onclick').match(/'([^']+)'/);
                const firstTabName = firstTabNameMatch ? firstTabNameMatch[1] : null;

                if (firstTabName) {
                    window.openTab({ currentTarget: firstTabButton }, firstTabName);
                    // console.log(`perfil_tabs.js: Activando pestaña por defecto: "${firstTabName}"`);
                } else {
                    // console.error('perfil_tabs.js: No se pudo extraer el nombre de la primera pestaña del atributo onclick. Fallback a clic nativo.');
                    firstTabButton.click(); 
                }
            } else {
                // console.error('perfil_tabs.js: No se encontró ningún botón de pestaña en el DOM. Asegúrate de que los elementos HTML estén correctos.');
            }
        }
    }); // Cierre de DOMContentLoaded
} // Cierre del guard
