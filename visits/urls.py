from django.urls import path
from visits import views

urlpatterns = [
    path('', views.visit_list, name='visit_list'),
    path('schedule/', views.schedule_visit, name='schedule_visit'),
    path('<str:visit_id>/', views.visit_detail, name='visit_detail'),
    path('<str:visit_id>/delete/', views.delete_visit, name='delete_visit'),
]
