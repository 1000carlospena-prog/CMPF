from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation'),
    path('nuevo/<int:user_id>/', views.start_conversation, name='start'),
    path('buscar/', views.search_users, name='search'),
]
