from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect

from .models import GRADO_NIVEL


class GradoRequiredMixin(LoginRequiredMixin):
    grado_minimo = 'v4'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.profile.tiene_acceso(self.grado_minimo):
            messages.error(request, 'No tienes permisos suficientes para acceder a esta sección.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class PublicadorRequiredMixin(GradoRequiredMixin):
    grado_minimo = 'v3'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        profile = request.user.profile
        if not profile.tiene_acceso(self.grado_minimo):
            messages.error(request, 'No tienes permisos suficientes para acceder a esta sección.')
            return redirect('home')
        if profile.grado == 'v3' and not profile.subscription_active:
            messages.error(request, 'Tu suscripción como proveedor (v3) no está activa. Renueva tu suscripción para publicar productos.')
            return redirect('upgrade')
        return super().dispatch(request, *args, **kwargs)
