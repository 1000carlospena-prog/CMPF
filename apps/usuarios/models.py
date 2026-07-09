from django.db import models
from django.contrib.auth.models import User

GRADO_CHOICES = [
    ('v00', 'v00 - Desarrollador'),
    ('v1', 'v1 - Super Admin'),
    ('v2', 'v2 - Administrador'),
    ('v3', 'v3 - Proveedor'),
    ('v4', 'v4 - Comprador'),
]

GRADO_NIVEL = {'v00': 0, 'v1': 1, 'v2': 2, 'v3': 3, 'v4': 4}

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    grado = models.CharField(max_length=3, choices=GRADO_CHOICES, default='v4')
    subscription_active = models.BooleanField(default=False)
    subscription_end = models.DateTimeField(null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.get_grado_display()}'

    @property
    def nivel(self):
        return GRADO_NIVEL.get(self.grado, 4)

    @property
    def puede_publicar(self):
        return self.grado in ('v00', 'v1', 'v2') or (self.grado == 'v3' and self.subscription_active)

    def tiene_acceso(self, grado_minimo):
        return self.nivel <= GRADO_NIVEL.get(grado_minimo, 4)
