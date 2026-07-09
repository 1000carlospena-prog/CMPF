import time
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


class TiempoRespuestaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        inicio = time.time()
        print(f'Petición recibida: {request.path}')

        response = self.get_response(request)

        fin = time.time()
        duracion = fin - inicio
        print(f'Tiempo de respuesta: {duracion:.2f} segundos')
        return response


class LoginRequiredMiddleware:
    """Redirige a login SOLO si la ruta NO está en la lista de rutas públicas"""

    RUTAS_PUBLICAS = [
        '/accounts/',
        '/admin/',
        '/static/',
        '/media/',
        '/productos/',
        '/libros/',
        '/registrarse/',
        '/upgrade/',
        '/verificar-codigo/',
        '/reenviar-codigo/',
        '/recuperar-contrasenia/',
        '/verificar-codigo-reset/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        es_publica = path == '/' or any(path.startswith(r) for r in self.RUTAS_PUBLICAS)

        if not request.user.is_authenticated and not es_publica:
            login_url = reverse('login')
            return redirect(f'{login_url}?next={request.path}')

        response = self.get_response(request)
        return response
