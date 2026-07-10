import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

GRADO_CHOICES = [
    ('v00', 'v00 - Desarrollador'),
    ('v1', 'v1 - Super Admin'),
    ('v2', 'v2 - Moderador'),
    ('v3', 'v3 - Proveedor'),
    ('v4', 'v4 - Comprador'),
]

GRADO_NIVEL = {'v00': 0, 'v1': 1, 'v2': 2, 'v3': 3, 'v4': 4}

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    grado = models.CharField(max_length=3, choices=GRADO_CHOICES, default='v4')
    nombre_real = models.CharField(max_length=150, blank=True, default='')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    super_id = models.PositiveIntegerField(null=True, blank=True, unique=True, verbose_name='Super Admin ID')
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
    MAX_INTENTOS = 5
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
    intentos_fallidos = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} - {self.code} ({self.proposito})'

    @staticmethod
    def generar_codigo():
        return f'{random.randint(100000, 999999)}'

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at and self.intentos_fallidos < self.MAX_INTENTOS

    def registrar_intento_fallido(self):
        self.intentos_fallidos += 1
        self.save(update_fields=['intentos_fallidos'])

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


class LoginAttempt(models.Model):
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ip_address', 'created_at']),
        ]

    @staticmethod
    def excede_limite(ip_address, max_intentos=5, ventana_minutos=15):
        desde = timezone.now() - timedelta(minutes=ventana_minutos)
        intentos = LoginAttempt.objects.filter(
            ip_address=ip_address,
            successful=False,
            created_at__gte=desde
        ).count()
        return intentos >= max_intentos

    @staticmethod
    def registrar(ip_address, username='', successful=False):
        return LoginAttempt.objects.create(
            ip_address=ip_address,
            username=username,
            successful=successful
        )
