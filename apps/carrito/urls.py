from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('ver/', views.ver_carrito, name='ver'),
    path('agregar/<int:content_type_id>/<int:object_id>/', views.agregar_al_carrito, name='agregar'),
    path('agregar/producto/<int:producto_id>/', views.agregar_producto, name='agregar_producto'),
    path('actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar'),
    path('eliminar/<int:item_id>/', views.eliminar_item_carrito, name='eliminar'),
    path('vaciar/', views.vaciar_carrito, name='vaciar'),
]