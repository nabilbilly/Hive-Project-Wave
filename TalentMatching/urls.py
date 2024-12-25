from django.urls import path
from . import views

app_name = 'talent_matching'

urlpatterns = [
    path('dashboard/', views.matching_dashboard, name='dashboard'),
    path('preferences/update/', views.update_preferences, name='update_preferences'),
    path('job/<int:job_id>/matches/', views.job_matches, name='job_matches'),
    path('refresh/', views.refresh_matches, name='refresh_matches'),
]
