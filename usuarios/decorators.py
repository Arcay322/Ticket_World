# usuarios/decorators.py
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages

def admin_required(view_func):
    @login_required(login_url=reverse_lazy(settings.LOGIN_URL))
    def _wrapped_view(request, *args, **kwargs):
        # --- TEMPORAL: LÍNEAS DE DEPURACIÓN EN EL DECORADOR ---
        print(f"\n--- DEBUG EN admin_required ---")
        print(f"URL solicitada: {request.path}")
        print(f"Usuario autenticado?: {request.user.is_authenticated}")
        if request.user.is_authenticated:
            print(f"Rol del usuario autenticado: {request.user.rol}")
        else:
            print(f"Usuario NO autenticado. Redirigiendo a LOGIN_URL.")
        print(f"--- FIN DEBUG ---\n")
        # --- FIN DE LÍNEAS DE DEPURACIÓN ---

        if request.user.rol != 'admin':
            messages.warning(request, "No tienes permisos para acceder a esta sección.")
            return redirect('usuarios:inicio')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
