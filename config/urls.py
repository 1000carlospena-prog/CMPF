# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
from apps.usuarios.views import perfil_usuario

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
    
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),

    # App: Usuarios
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),

    # Perfiles públicos
    path('perfil/<int:user_id>/', perfil_usuario, name='perfil_usuario'),

    # Chat / Mensajería
    path('chat/', include('apps.chat.urls', namespace='chat')),

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
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Órdenes
    path('ordenes/', include('apps.ordenes.urls', namespace='ordenes')),

    # Blog
    path('blog/', include('apps.blog.urls', namespace='blog')),

    # Páginas estáticas
    path('acerca-de/', views.acerca_de, name='acerca_de'),
    path('contacto/', views.contacto, name='contacto'),
    path('faq/', views.faq, name='faq'),
    path('terminos/', views.terminos, name='terminos'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)