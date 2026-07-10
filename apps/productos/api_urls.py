from django.urls import path, include
from apps.productos.views import ProductoViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'productos', ProductoViewset)

urlpatterns = [
    path('', include(router.urls)),
]
