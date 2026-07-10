from django.urls import path
from . import views

app_name = 'ordenes'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('historial/', views.historial, name='historial'),
    path('<int:orden_id>/', views.detalle, name='detalle'),
]
