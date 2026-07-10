from django.urls import path
from apps.catalogo_libros import views

urlpatterns = [
    path('', views.listaLibros, name='listalibros'),
    path('<int:id>/', views.detalle_libro, name='detalle_libro'),
    path('crear/', views.crearLibro, name='crearLibro'),
]