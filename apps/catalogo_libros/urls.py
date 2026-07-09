# apps/catalogo_libros/urls.py
from django.urls import path
from apps.catalogo_libros import views

urlpatterns = [
    path('', views.listaLibros, name='listalibros'),
    path('<int:id>/', views.detalle_libro, name='detalle_libro'),
    path('crear/', views.crearLibro, name='crearLibro'),
    # ✅ ELIMINAR estas líneas (ya están en config/urls.py)
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
]