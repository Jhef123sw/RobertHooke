from django.http import HttpResponseForbidden
from functools import wraps

def estudiante_tipo_requerido(tipos_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.tipo_estudiante in tipos_permitidos:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return _wrapped_view
    return decorator