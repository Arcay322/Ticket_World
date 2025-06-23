// static/js/admin_menu_sorter.js

document.addEventListener("DOMContentLoaded", function () {
    const sidebarMenu = document.querySelector("ul.nav-sidebar");
    if (!sidebarMenu) return;

    // --- LÓGICA DE NOTIFICACIONES (MODIFICADA) ---
    // 1. Ya no buscamos un div. Leemos la variable global que creamos en base.html
    const pendingEventsCount = window.PENDING_COUNTS?.events || 0;
    const pendingRequestsCount = window.PENDING_COUNTS?.requests || 0;

    // 2. La función para crear la insignia se mantiene igual
    function createNotificationBadge(count) {
        if (count > 0) {
            const badge = document.createElement("span");
            badge.className = "menu-notification-badge";
            badge.textContent = count;
            return badge;
        }
        return null;
    }
    // --- FIN LÓGICA DE NOTIFICACIONES ---


    // --- LÓGICA DE REORDENAMIENTO (EXISTENTE) ---
    const eventosPendientesLink = sidebarMenu.querySelector(
        'a[href*="/admin/tickets/evento/?aprobado__exact=0"]'
    );
    const solicitudesLink = sidebarMenu.querySelector(
        'a[href*="/admin/usuarios/solicitudproveedor/"]'
    );

    // Añadimos las insignias a los enlaces
    if (eventosPendientesLink && pendingEventsCount > 0) {
        const badge = createNotificationBadge(pendingEventsCount);
        if (badge) eventosPendientesLink.appendChild(badge);
    }

    if (solicitudesLink && pendingRequestsCount > 0) {
        const badge = createNotificationBadge(pendingRequestsCount);
        if (badge) solicitudesLink.appendChild(badge);
    }
    
    // El resto de la lógica para reordenar el menú se mantiene igual
    const newHeader = document.createElement("li");
    newHeader.className = "nav-header";
    newHeader.textContent = "TAREAS IMPORTANTES";

    const panelDeControl = sidebarMenu.querySelector('a[href="/admin/"]');
    if (panelDeControl) {
        const panelDeControlLi = panelDeControl.closest(".nav-item");
        panelDeControlLi.after(newHeader);
        if (solicitudesLink) {
            newHeader.after(solicitudesLink.closest(".nav-item"));
        }
        if (eventosPendientesLink) {
            newHeader.after(eventosPendientesLink.closest(".nav-item"));
        }
    }
});