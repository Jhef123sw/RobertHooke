from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

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

def datos_actualizados_requerido(redirect_url_name='actualizar_datos'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and getattr(request.user, 'actualizado', '') == 'actualizado':
                return view_func(request, *args, **kwargs)
            else:
                messages.warning(request, "⚠️ Por favor, actualiza tus datos para continuar, solo se hace una sola vez.")
                return redirect(redirect_url_name)
        return _wrapped_view
    return decorator