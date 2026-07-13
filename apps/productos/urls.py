from django.urls import path
from .views import (
    ProductoDetalle, ProductoActualizar, ProductoVista,
    ProductosEliminar, ProductoCrear, eliminar_imagen,
    agregar_resena, toggle_deseo, lista_deseos,
    mi_inventario, ajustar_stock,
)

app_name = 'productos'

urlpatterns = [
    path('', ProductoVista.as_view(), name='lista_productos'),
    path('<int:pk>/', ProductoDetalle.as_view(), name='detalle_producto'),
    path('crear/', ProductoCrear.as_view(), name='crear_producto'),
    path('actualizar/<int:pk>/', ProductoActualizar.as_view(), name='actualizar_producto'),
    path('eliminar/<int:pk>/', ProductosEliminar.as_view(), name='eliminar_producto'),
    path('eliminar-imagen/<int:imagen_id>/', eliminar_imagen, name='eliminar_imagen'),
    path('<int:producto_id>/resena/', agregar_resena, name='agregar_resena'),
    path('<int:producto_id>/deseo/', toggle_deseo, name='toggle_deseo'),
    path('lista-deseos/', lista_deseos, name='lista_deseos'),
    path('inventario/', mi_inventario, name='mi_inventario'),
    path('inventario/<int:producto_id>/ajustar/', ajustar_stock, name='ajustar_stock'),
]
