from django.urls import path
from dashboard import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard-alt'),  # Alternative URL for explicit redirect
    path('analytics/', views.analytics, name='analytics'),
]
