from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def admin_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.rol != 'admin':
            return HttpResponseForbidden("No tienes permiso para acceder a esta vista.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
