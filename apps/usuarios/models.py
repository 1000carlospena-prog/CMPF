import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

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


class VerificationCode(models.Model):
    PROPOSITOS = [
        ('register', 'Registro'),
        ('reset', 'Restablecer contraseña'),
    ]

    email = models.EmailField()
    code = models.CharField(max_length=6)
    proposito = models.CharField(max_length=10, choices=PROPOSITOS)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} - {self.code} ({self.proposito})'

    @staticmethod
    def generar_codigo():
        return f'{random.randint(100000, 999999)}'

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

    @staticmethod
    def crear_codigo(email, proposito):
        codigo = VerificationCode.generar_codigo()
        VerificationCode.objects.filter(email=email, proposito=proposito, is_used=False).update(is_used=True)
        return VerificationCode.objects.create(
            email=email,
            code=codigo,
            proposito=proposito,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
