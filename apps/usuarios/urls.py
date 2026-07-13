from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.listar_usuarios, name='lista'),
    path('crear/', views.crear_usuario, name='crear'),
    path('mi-perfil/', views.editar_mi_perfil, name='editar_mi_perfil'),
    path('explorar/', views.explorar_usuarios, name='explorar'),
    path('<int:user_id>/', views.detalle_usuario, name='detalle'),
    path('<int:user_id>/editar/', views.editar_usuario, name='editar'),
    path('<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar'),
    path('<int:user_id>/seguir/', views.seguir_usuario, name='seguir'),
    path('<int:user_id>/dejar-seguir/', views.dejar_de_seguir, name='dejar_seguir'),
]

# Profile (public) — outside app namespace for clean URLs

