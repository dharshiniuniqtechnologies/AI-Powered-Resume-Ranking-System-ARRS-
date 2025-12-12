from django.urls import path
from .views import rank_resumes, test_ranking

urlpatterns = [
    path('test/', test_ranking, name='test-ranking'),
    path('rank/<int:job_id>/', rank_resumes, name='rank-resumes'),
]
