from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:

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


class TiempoRespuestaMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import time
        start = time.time()
        response = self.get_response(request)
        end = time.time()
        print(f"Tiempo de respuesta: {end - start:.3f}s")
        return response
