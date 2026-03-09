from django.urls import path
from agents import views

urlpatterns = [
    path('', views.agent_list, name='agent_list'),
    path('create/', views.agent_create, name='agent_create'),
    path('<str:agent_id>/edit/', views.agent_edit, name='agent_edit'),
    path('<str:agent_id>/delete/', views.agent_delete, name='agent_delete'),
]
