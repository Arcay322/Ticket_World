# tickets/utils.py

from tickets.models import Evento, AdminNotification # Importa Evento y el nuevo AdminNotification
from usuarios.models import SolicitudProveedor # Importa tu modelo SolicitudProveedor
from django.contrib.auth import get_user_model # Necesario para get_unread_notifications_count

# Función para contar Eventos Pendientes de Aprobación
def get_pending_events_count():
    return Evento.objects.filter(aprobado=False).count()

# Función para contar Solicitudes de Proveedores Pendientes
def get_pending_supplier_requests_count():
    return SolicitudProveedor.objects.filter(aprobado=False).count()

# Función para contar TODAS las notificaciones de Admin no leídas para el usuario actual

def get_unread_admin_notifications_count(request):
    # --- MENSAJES DE DEPURACIÓN (TEMPORALES) ---
    print("\n--- INICIO DEPURACIÓN get_unread_admin_notifications_count ---")
    if not hasattr(request, 'user'):
        print("DEBUG: El objeto request no tiene atributo 'user'.")
        print("--- FIN DEPURACIÓN ---\n")
        return 0

    if not request.user.is_authenticated:
        print(f"DEBUG: Usuario no autenticado ({request.user}).")
        print("--- FIN DEPURACIÓN ---\n")
        return 0

    User = get_user_model()
    if not request.user.is_superuser: # Si estas notificaciones son SÓLO para superusuarios
        print(f"DEBUG: Usuario '{request.user.username}' no es superusuario. No se mostrarán notificaciones de admin.")
        print("--- FIN DEPURACIÓN ---\n")
        return 0

    try:
        count = AdminNotification.objects.filter(recipient=request.user, read=False).count()
        print(f"DEBUG: Conteo de notificaciones no leídas para '{request.user.username}': {count}")
        print("--- FIN DEPURACIÓN ---\n")
        return count
    except Exception as e:
        print(f"ERROR: Falló el conteo de notificaciones de admin: {e}")
        print("--- FIN DEPURACIÓN ---\n")
        return 0