// static/js/admin_notifications.js

document.addEventListener("DOMContentLoaded", function () {
    console.log("Admin Enhancer Script: DOM cargado.");

    // Damos un poco de tiempo para que todo se renderice
    setTimeout(function() {
        console.log("Admin Enhancer Script: Ejecutando script de menú...");

        // --- !! POSIBLE PUNTO DE CAMBIO !! ---
        // Busca el contenedor principal del menú lateral.
        // Reemplaza 'ul.nav-sidebar' si encontraste una clase diferente.
        const sidebarMenu = document.querySelector("ul.nav-sidebar"); 
        if (!sidebarMenu) {
            console.error("ERROR: No se encontró el menú principal. Revisa el selector 'ul.nav-sidebar'.");
            return;
        }
        console.log("ÉXITO: Menú principal encontrado.", sidebarMenu);

        // El resto del script...
        const pendingEventsCount = window.PENDING_COUNTS?.events || 0;
        const pendingRequestsCount = window.PENDING_COUNTS?.requests || 0;

        function createNotificationBadge(count) {
            if (count > 0) {
                const badge = document.createElement("span");
                badge.className = "menu-notification-badge";
                badge.textContent = count;
                return badge;
            }
            return null;
        }

        function createCustomMenuLink(url, iconClass, text) {
            const li = document.createElement('li');
            li.className = 'nav-item';
            const a = document.createElement('a');
            a.href = url;
            a.className = 'nav-link';
            const i = document.createElement('i');
            i.className = 'nav-icon ' + iconClass;
            const p = document.createElement('p');
            p.textContent = text;
            a.appendChild(i);
            a.appendChild(p);
            li.appendChild(a);
            return { listItem: li, link: a };
        }

        // Buscamos el grupo "Tickets" para añadir nuestros enlaces personalizados
        const ticketsAnchor = sidebarMenu.querySelector('a[href*="/admin/tickets/"]');
        if (!ticketsAnchor) {
             console.error("ERROR: No se encontró ningún enlace de la app 'tickets' para anclar los nuevos enlaces.");
             return;
        }
        console.log("ÉXITO: Encontrado anclaje en 'Tickets'.");

        const ticketsUl = ticketsAnchor.closest('.nav-treeview');
        if (!ticketsUl) {
            console.error("ERROR: No se encontró el sub-menú (ul.nav-treeview) para la app 'tickets'.");
            return;
        }
        
        // Creamos y añadimos los enlaces personalizados
        const eventos = createCustomMenuLink('/admin/tickets/evento/?aprobado__exact=0', 'fas fa-clock', 'Eventos por Aprobar');
        const opiniones = createCustomMenuLink('/admin/tickets/opinion/?estado__exact=pendiente', 'fas fa-comment-dots', 'Opiniones Pendientes');
        
        const badgeEventos = createNotificationBadge(pendingEventsCount);
        if (badgeEventos) eventos.link.appendChild(badgeEventos);
        
        ticketsUl.appendChild(eventos.listItem);
        ticketsUl.appendChild(opiniones.listItem);
        console.log("ÉXITO: Enlaces personalizados añadidos a 'Tickets'.");
        
        // Añadimos la insignia al enlace de Solicitudes de Proveedores
        const solicitudesLink = sidebarMenu.querySelector('a[href*="/admin/usuarios/solicitudproveedor/"]');
        if (solicitudesLink) {
            const badgeRequests = createNotificationBadge(pendingRequestsCount);
            if (badgeRequests) solicitudesLink.appendChild(badgeRequests);
            console.log("ÉXITO: Insignia añadida a 'Solicitudes de Proveedores'.");
        } else {
            console.warn("AVISO: No se encontró el enlace de 'Solicitudes de Proveedores'.");
        }

    }, 500); // Aumentamos la espera a medio segundo para estar seguros
});