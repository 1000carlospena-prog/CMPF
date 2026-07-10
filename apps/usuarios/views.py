from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .decorators import grado_required
from .models import Profile, GRADO_CHOICES, GRADO_NIVEL


def _usuarios_visibles(request):
    usuarios = User.objects.all().order_by('username')
    grado = request.user.profile.grado
    if grado == 'v2':
        usuarios = usuarios.filter(profile__grado__in=['v3', 'v4'])
    elif grado == 'v1':
        usuarios = usuarios.exclude(profile__grado__in=['v00', 'v1'])
    return usuarios


def _puede_modificar(request, usuario):
    grado_actual = request.user.profile.grado
    grado_target = usuario.profile.grado
    if grado_actual == 'v00':
        return True
    if grado_actual == 'v1' and grado_target in ('v2', 'v3', 'v4'):
        return True
    if grado_actual == 'v2' and grado_target in ('v3', 'v4'):
        return True
    return False


def _grados_permitidos(request):
    grado = request.user.profile.grado
    if grado == 'v00':
        return GRADO_CHOICES
    if grado == 'v1':
        return [g for g in GRADO_CHOICES if g[0] in ('v2', 'v3', 'v4')]
    if grado == 'v2':
        return [g for g in GRADO_CHOICES if g[0] in ('v3', 'v4')]
    return []


@grado_required('v2')
def listar_usuarios(request):
    usuarios = _usuarios_visibles(request)
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})


@grado_required('v2')
def detalle_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if not _puede_modificar(request, usuario):
        messages.error(request, 'No tienes permiso para ver este usuario.')
        return redirect('usuarios:lista')
    return render(request, 'usuarios/detalle.html', {'usuario': usuario})


@grado_required('v2')
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if not _puede_modificar(request, usuario):
        messages.error(request, 'No tienes permiso para modificar este usuario.')
        return redirect('usuarios:lista')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        grado = request.POST.get('grado')

        if not username:
            messages.error(request, 'El nombre de usuario es obligatorio.')
            return redirect('usuarios:editar', user_id=usuario.id)

        if username != usuario.username and User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return redirect('usuarios:editar', user_id=usuario.id)

        if grado and grado not in dict(GRADO_CHOICES):
            messages.error(request, 'Grado no válido.')
            return redirect('usuarios:editar', user_id=usuario.id)

        if grado:
            grados_ok = _grados_permitidos(request)
            if not any(g[0] == grado for g in grados_ok):
                messages.error(request, 'No tienes permiso para asignar ese grado.')
                return redirect('usuarios:editar', user_id=usuario.id)
            if grado == 'v00' and usuario.profile.grado != 'v00' and User.objects.filter(profile__grado='v00').exists():
                messages.error(request, 'Ya existe un usuario Desarrollador (v00). Solo puede haber uno.')
                return redirect('usuarios:editar', user_id=usuario.id)
            usuario.profile.grado = grado
            usuario.profile.save()

        usuario.username = username
        usuario.email = email
        if password:
            usuario.password = make_password(password)
        usuario.save()

        messages.success(request, f'✅ Usuario "{usuario.username}" actualizado.')
        return redirect('usuarios:detalle', user_id=usuario.id)

    return render(request, 'usuarios/editar.html', {
        'usuario': usuario,
        'grados': _grados_permitidos(request),
    })


@grado_required('v2')
def crear_usuario(request):
    grados_ok = _grados_permitidos(request)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        grado = request.POST.get('grado', 'v4')

        if not all([username, password]):
            messages.error(request, 'Usuario y contraseña son obligatorios.')
            return redirect('usuarios:crear')

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('usuarios:crear')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe.')
            return redirect('usuarios:crear')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado.')
            return redirect('usuarios:crear')

        if grado == 'v00' and User.objects.filter(profile__grado='v00').exists():
            messages.error(request, 'Ya existe un usuario Desarrollador (v00). Solo puede haber uno.')
            return redirect('usuarios:crear')

        if not any(g[0] == grado for g in grados_ok):
            messages.error(request, 'No tienes permiso para crear usuarios con ese grado.')
            return redirect('usuarios:crear')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.profile.grado = grado
        user.profile.save()
        messages.success(request, f'✅ Usuario "{username}" creado con grado {grado}.')
        return redirect('usuarios:lista')

    return render(request, 'usuarios/crear.html', {'grados': grados_ok})


@grado_required('v2')
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if usuario == request.user:
        messages.error(request, 'No puedes eliminarte a ti mismo.')
        return redirect('usuarios:lista')
    if not _puede_modificar(request, usuario):
        messages.error(request, 'No tienes permiso para eliminar este usuario.')
        return redirect('usuarios:lista')
    username = usuario.username
    usuario.delete()
    messages.success(request, f'🗑️ Usuario "{username}" eliminado.')
    return redirect('usuarios:lista')
