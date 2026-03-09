from django.urls import path
from leads import views

urlpatterns = [
    path('', views.lead_list, name='lead_list'),
    path('capture/', views.lead_capture, name='lead_capture'),
    path('capture/success/', views.lead_capture_success, name='lead_capture_success'),
    path('pipeline/', views.pipeline_view, name='pipeline_view'),
    path('followups/', views.followup_list, name='followup_list'),
    path('followups/<str:followup_id>/complete/', views.complete_followup, name='complete_followup'),
    path('<str:lead_id>/', views.lead_detail, name='lead_detail'),
    path('<str:lead_id>/update-stage/', views.update_stage, name='update_stage'),
    path('<str:lead_id>/delete/', views.delete_lead, name='delete_lead'),
]
