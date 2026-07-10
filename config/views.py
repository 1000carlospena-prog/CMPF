import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

from apps.usuarios.models import VerificationCode, LoginAttempt
from apps.usuarios.utils import validar_contrasenia, enviar_codigo_email
from apps.productos.models import Producto, Categoria
from apps.blog.models import Post

logger = logging.getLogger('cmpf.security')


def home(request):
    productos_destacados = Producto.objects.filter(destacado=True, disponible=True)[:8]
    productos_oferta = Producto.objects.exclude(precio_oferta__isnull=True)[:4]
    categorias = Categoria.objects.filter(activa=True, padre__isnull=True)[:6]
    posts_recientes = Post.objects.filter(publicado=True)[:3]
    ultimos_productos = Producto.objects.filter(disponible=True).order_by('-creado')[:4]

    from apps.catalogo_libros.models import Libros

    context = {
        'productos_destacados': productos_destacados,
        'productos_oferta': productos_oferta,
        'categorias_home': categorias,
        'posts_recientes': posts_recientes,
        'ultimos_productos': ultimos_productos,
        'total_productos': Producto.objects.count(),
        'total_libros': Libros.objects.count(),
        'total_categorias': Categoria.objects.filter(activa=True).count(),
    }
    return render(request, 'home.html', context)


def upgrade(request):
    return render(request, 'upgrade.html')


def registrarse(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        nombre_real = request.POST.get('nombre_real', '').strip()
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

        if not email or '@gmail.com' not in email.lower():
            messages.error(request, 'Debes ingresar un correo de Gmail válido.')
            return redirect('registrarse')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
            return redirect('registrarse')

        errores = validar_contrasenia(password)
        if errores:
            for e in errores:
                messages.error(request, e)
            return redirect('registrarse')

        if tipo not in ('v3', 'v4'):
            tipo = 'v4'

        vc = VerificationCode.crear_codigo(email, 'register')

        try:
            enviar_codigo_email(email, vc.code, 'register')
        except Exception as e:
            logger.warning(f'Error enviando email a {email}: {e}')
            messages.warning(request, f'No se pudo enviar el email. Tu código es: {vc.code}')
            messages.info(request, 'Configura EMAIL_HOST_USER/PASSWORD en Render para envío automático.')

        hashed = make_password(password)
        request.session['registro_temp'] = {
            'username': username,
            'nombre_real': nombre_real,
            'email': email,
            'password_hash': hashed,
            'tipo': tipo,
            'code_id': vc.id,
        }
        request.session['email_para_verificar'] = email
        return redirect('verificar_codigo')

    return render(request, 'registration/registrarse.html')


def verificar_codigo(request):
    temp = request.session.get('registro_temp')
    email = request.session.get('email_para_verificar')

    if not temp or not email:
        messages.error(request, 'Sesión expirada. Regístrate de nuevo.')
        return redirect('registrarse')

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()

        try:
            vc = VerificationCode.objects.get(id=temp['code_id'], email=email, code=codigo)
            if not vc.is_valid():
                messages.error(request, 'Código expirado o demasiados intentos. Solicita uno nuevo.')
                logger.warning(f'Código inválido o bloqueado para {email}')
                return redirect('registrarse')
        except VerificationCode.DoesNotExist:
            msg = 'Código incorrecto.'
            if temp['code_id']:
                try:
                    vc2 = VerificationCode.objects.get(id=temp['code_id'])
                    vc2.registrar_intento_fallido()
                    if vc2.intentos_fallidos >= VerificationCode.MAX_INTENTOS:
                        msg = 'Demasiados intentos. Solicita un nuevo código.'
                        logger.warning(f'Código bloqueado por intentos: {email}')
                except VerificationCode.DoesNotExist:
                    pass
            messages.error(request, msg)
            return redirect('verificar_codigo')

        vc.is_used = True
        vc.save()

        user = User(username=temp['username'], email=temp['email'])
        user.password = temp['password_hash']
        user.save()
        user.profile.grado = temp['tipo']
        user.profile.nombre_real = temp.get('nombre_real', '')
        user.profile.save()

        LoginAttempt.registrar(request.META.get('REMOTE_ADDR', ''), user.username, successful=True)
        logger.info(f'Usuario registrado y verificado: {user.username}')

        del request.session['registro_temp']
        del request.session['email_para_verificar']

        login(request, user)

        if temp['tipo'] == 'v3':
            messages.success(request, 'Cuenta verificada. Ahora completa tu suscripción para publicar productos.')
            return redirect('upgrade')
        else:
            messages.success(request, f'✅ Cuenta verificada. ¡Bienvenido {temp["username"]}!')
            return redirect('home')

    return render(request, 'usuarios/verificar_codigo.html', {'email': email})


def reenviar_codigo(request):
    temp = request.session.get('registro_temp')
    email = request.session.get('email_para_verificar')

    if not temp or not email:
        messages.error(request, 'Sesión expirada.')
        return redirect('registrarse')

    vc = VerificationCode.crear_codigo(email, 'register')
    temp['code_id'] = vc.id
    request.session['registro_temp'] = temp

    try:
        enviar_codigo_email(email, vc.code, 'register')
        messages.success(request, 'Nuevo código enviado a tu correo.')
    except Exception:
        messages.error(request, 'Error al enviar el código.')
        return redirect('registrarse')

    return redirect('verificar_codigo')


def recuperar_contrasenia(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, 'Ingresa tu correo electrónico.')
            return redirect('recuperar_contrasenia')

        if not User.objects.filter(email=email).exists():
            messages.error(request, 'No existe una cuenta con ese correo.')
            return redirect('recuperar_contrasenia')

        vc = VerificationCode.crear_codigo(email, 'reset')

        try:
            enviar_codigo_email(email, vc.code, 'reset')
        except Exception as e:
            logger.warning(f'Error enviando email reset a {email}: {e}')
            messages.warning(request, f'No se pudo enviar el email. Tu código es: {vc.code}')

        request.session['reset_email'] = email
        request.session['reset_code_id'] = vc.id
        messages.success(request, 'Código enviado a tu correo.')
        return redirect('verificar_codigo_reset')

    return render(request, 'usuarios/recuperar_contrasenia.html')


def verificar_codigo_reset(request):
    email = request.session.get('reset_email')
    code_id = request.session.get('reset_code_id')

    if not email or not code_id:
        messages.error(request, 'Sesión expirada. Solicita el código de nuevo.')
        return redirect('recuperar_contrasenia')

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        try:
            vc = VerificationCode.objects.get(id=code_id, email=email, code=codigo, proposito='reset')
            if not vc.is_valid():
                messages.error(request, 'Código expirado o bloqueado. Solicita uno nuevo.')
                logger.warning(f'Reset code invalid/blocked for {email}')
                return redirect('recuperar_contrasenia')
        except VerificationCode.DoesNotExist:
            msg = 'Código incorrecto.'
            if code_id:
                try:
                    vc2 = VerificationCode.objects.get(id=code_id)
                    vc2.registrar_intento_fallido()
                    if vc2.intentos_fallidos >= VerificationCode.MAX_INTENTOS:
                        msg = 'Código bloqueado por demasiados intentos.'
                        logger.warning(f'Reset code brute-force blocked: {email}')
                except VerificationCode.DoesNotExist:
                    pass
            messages.error(request, msg)
            return redirect('verificar_codigo_reset')

        if not password:
            messages.error(request, 'Ingresa una nueva contraseña.')
            return redirect('verificar_codigo_reset')

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('verificar_codigo_reset')

        errores = validar_contrasenia(password)
        if errores:
            for e in errores:
                messages.error(request, e)
            return redirect('verificar_codigo_reset')

        vc.is_used = True
        vc.save()

        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        del request.session['reset_email']
        del request.session['reset_code_id']

        LoginAttempt.registrar(request.META.get('REMOTE_ADDR', ''), user.username, successful=True)
        logger.info(f'Password reset successful: {user.username}')

        login(request, user)
        messages.success(request, '✅ Contraseña restablecida correctamente.')
        return redirect('home')

    return render(request, 'usuarios/restablecer_contrasenia.html', {'email': email})


def upgrade_solicitar(request):
    if request.method == 'POST' and request.user.is_authenticated:
        profile = request.user.profile
        profile.grado = 'v3'
        profile.subscription_active = True
        profile.subscription_end = timezone.now() + timedelta(days=30)
        profile.save()
        messages.success(request, '🎉 ¡Suscripción activada! Ahora eres v3 - Proveedor. Puedes publicar productos.')
    return redirect('upgrade')


def login_con_rate_limit(request):
    ip = request.META.get('REMOTE_ADDR', '')

    if LoginAttempt.excede_limite(ip):
        logger.warning(f'Login bloqueado por rate-limit: {ip}')
        messages.error(request, 'Demasiados intentos. Espera 15 minutos.')
        return redirect('login')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            LoginAttempt.registrar(ip, user.username, successful=True)
            logger.info(f'Login exitoso: {user.username} desde {ip}')
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            LoginAttempt.registrar(ip, username, successful=False)
            logger.warning(f'Login fallido: {username} desde {ip}')
            messages.error(request, 'Usuario o contraseña incorrectos.')

    from django.contrib.auth.forms import AuthenticationForm
    form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def acerca_de(request):
    return render(request, 'pages/acerca_de.html')


def contacto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        email = request.POST.get('email', '')
        mensaje = request.POST.get('mensaje', '')
        try:
            send_mail(
                f'Contacto CMPF - {nombre}',
                f'De: {nombre} ({email})\n\n{mensaje}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'Mensaje enviado. Te responderemos pronto.')
        except Exception:
            messages.error(request, 'Error al enviar el mensaje. Intenta de nuevo.')
        return redirect('contacto')
    return render(request, 'pages/contacto.html')


def faq(request):
    return render(request, 'pages/faq.html')


def terminos(request):
    return render(request, 'pages/terminos.html')
