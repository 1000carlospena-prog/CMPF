from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

def grado_required(grado_minimo):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f'{reverse("login")}?next={request.path}')
            if not request.user.profile.tiene_acceso(grado_minimo):
                messages.error(request, 'No tienes permisos suficientes para acceder a esta sección.')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
