from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('jobs/', views.job_search, name='job_search'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('jobs/<int:job_id>/report/', views.report_job, name='report_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('preferences/', views.update_preferences, name='update_preferences'),
    path('job/', views.job_view, name='job_view'),
]