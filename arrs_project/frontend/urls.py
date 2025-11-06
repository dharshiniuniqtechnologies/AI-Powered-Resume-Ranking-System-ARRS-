from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('jobs/', views.job_list, name='job-list'),
    path('upload/', views.upload_resume, name='upload-resume'),
    path('ranking/<int:job_id>/', views.ranking_results, name='ranking-results'),

    path('dashboard/', views.recruiter_dashboard, name='recruiter-dashboard'),
    path('recruiter/add-job/', views.create_job, name='create_job'),
    path('recruiter/edit-job/<int:job_id>/', views.edit_job, name='edit_job'),
    path('recruiter/delete-job/<int:job_id>/', views.delete_job, name='delete_job'),
    
    path('dashboard/rank/<int:job_id>/', views.trigger_ranking, name='trigger-ranking'),
    path("profile/", views.profile_view, name="profile"),
    
]
