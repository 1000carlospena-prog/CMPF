import re
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def validar_contrasenia(password):
    errores = []
    if len(password) < 8:
        errores.append('La contraseña debe tener al menos 8 caracteres.')
    if not re.search(r'[A-Z]', password):
        errores.append('Debe contener al menos una mayúscula.')
    if not re.search(r'[a-z]', password):
        errores.append('Debe contener al menos una minúscula.')
    if not re.search(r'[0-9]', password):
        errores.append('Debe contener al menos un número.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_]', password):
        errores.append('Debe contener al menos un carácter especial (!@#$%^&* etc.).')
    return errores


def enviar_codigo_email(email, codigo, proposito):
    asunto = 'Tu código de verificación - CMPF'
    if proposito == 'reset':
        asunto = 'Restablecer tu contraseña - CMPF'

    mensaje = f'Tu código de verificación es: {codigo}\n\nEste código expira en 10 minutos.'
    html = render_to_string('usuarios/email_codigo.html', {
        'codigo': codigo,
        'proposito': proposito,
    })

    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=html,
        fail_silently=False,
    )
