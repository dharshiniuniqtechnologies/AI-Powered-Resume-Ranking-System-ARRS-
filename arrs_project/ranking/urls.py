from django.urls import path
from .views import rank_resumes, test_ranking, get_ranked_results

urlpatterns = [
    path('test/', test_ranking, name='test-ranking'),
    path('rank/<int:job_id>/', rank_resumes, name='rank-resumes'),
    path('results/<int:job_id>/', get_ranked_results, name='get-ranked-results'),

]
