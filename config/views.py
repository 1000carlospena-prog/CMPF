from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def home(request):
    context = {
        'title': 'CMPF - Sistema Integrado',
        'apps': [
            {
                'name': 'Productos',
                'description': 'Gestión de inventario de productos',
                'url': 'productos:lista_productos',
                'icon': '📦',
                'color': 'blue',
            },
            {
                'name': 'Librería',
                'description': 'Catálogo de libros y gestión literaria',
                'url': 'listalibros',
                'icon': '📚',
                'color': 'green',
            }
        ]
    }
    return render(request, 'home.html', context)


def upgrade(request):
    return render(request, 'upgrade.html')


def registrarse(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        tipo = request.POST.get('tipo', 'v4')

        if not all([username, password]):
            messages.error(request, 'Usuario y contraseña son obligatorios.')
            return redirect('registrarse')

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('registrarse')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe.')
            return redirect('registrarse')

        if tipo not in ('v3', 'v4'):
            tipo = 'v4'

        user = User.objects.create_user(username=username, email=email, password=password)
        user.profile.grado = tipo
        user.profile.save()

        login(request, user)

        if tipo == 'v3':
            messages.success(request, 'Cuenta creada. Ahora completa tu suscripción para publicar productos.')
            return redirect('upgrade')
        else:
            messages.success(request, f'✅ Cuenta creada. Bienvenido {username}!')
            return redirect('home')

    return render(request, 'registration/registrarse.html')


def upgrade_solicitar(request):
    if request.method == 'POST' and request.user.is_authenticated:
        profile = request.user.profile
        profile.grado = 'v3'
        profile.subscription_active = True
        profile.subscription_end = timezone.now() + timedelta(days=30)
        profile.save()
        messages.success(request, '🎉 ¡Suscripción activada! Ahora eres v3 - Proveedor. Puedes publicar productos.')
    return redirect('upgrade')