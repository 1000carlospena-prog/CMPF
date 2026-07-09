from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.listar_usuarios, name='lista'),
    path('crear/', views.crear_usuario, name='crear'),
    path('<int:user_id>/', views.detalle_usuario, name='detalle'),
    path('<int:user_id>/editar/', views.editar_usuario, name='editar'),
    path('<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar'),
]
