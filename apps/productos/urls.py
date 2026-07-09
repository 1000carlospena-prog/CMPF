from django.urls import path
from .views import (
    ProductoDetalle, ProductoActualizar, ProductoVista,
    ProductosEliminar, ProductoCrear, eliminar_imagen
)

app_name = 'productos'

urlpatterns = [
    path('', ProductoVista.as_view(), name='lista_productos'),
    path('<int:pk>/', ProductoDetalle.as_view(), name='detalle_producto'),
    path('crear/', ProductoCrear.as_view(), name='crear_producto'),
    path('actualizar/<int:pk>/', ProductoActualizar.as_view(), name='actualizar_producto'),
    path('eliminar/<int:pk>/', ProductosEliminar.as_view(), name='eliminar_producto'),
    # ✅ Nueva URL para eliminar imagen
    path('eliminar-imagen/<int:imagen_id>/', eliminar_imagen, name='eliminar_imagen'),
]