from django.urls import path
from .views import BlogLista, BlogDetalle, agregar_comentario

app_name = 'blog'

urlpatterns = [
    path('', BlogLista.as_view(), name='lista'),
    path('<slug:slug>/', BlogDetalle.as_view(), name='detalle'),
    path('<slug:slug>/comentar/', agregar_comentario, name='comentar'),
]
