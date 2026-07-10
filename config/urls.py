# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Autenticación
    path('accounts/login/', views.login_con_rate_limit, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Portal CMPF
    path('', views.home, name='home'),
    path('upgrade/', views.upgrade, name='upgrade'),
    path('upgrade/solicitar/', views.upgrade_solicitar, name='upgrade_solicitar'),
    path('registrarse/', views.registrarse, name='registrarse'),
    
    # App: Dashboard
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),  # ✅ AGREGAR

    # App: Usuarios
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),

    # Verificación de email
    path('verificar-codigo/', views.verificar_codigo, name='verificar_codigo'),
    path('reenviar-codigo/', views.reenviar_codigo, name='reenviar_codigo'),
    path('recuperar-contrasenia/', views.recuperar_contrasenia, name='recuperar_contrasenia'),
    path('verificar-codigo-reset/', views.verificar_codigo_reset, name='verificar_codigo_reset'),
    
    # App: Carrito
    path('carrito/', include('apps.carrito.urls', namespace='carrito')),
    
    # App: Productos
    path('productos/', include('apps.productos.urls', namespace='productos')),
    
    # App: Librería
    path('libros/', include('apps.catalogo_libros.urls')),
    
    # API REST
    path('api/', include('apps.productos.api_urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api-token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)