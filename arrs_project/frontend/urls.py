from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job-list'),
    path('upload/', views.upload_resume, name='upload-resume'),
    path('ranking/<int:job_id>/', views.ranking_results, name='ranking-results'),

    path('dashboard/', views.recruiter_dashboard, name='recruiter-dashboard'),
    path('dashboard/rank/<int:job_id>/', views.trigger_ranking, name='trigger-ranking'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

]
