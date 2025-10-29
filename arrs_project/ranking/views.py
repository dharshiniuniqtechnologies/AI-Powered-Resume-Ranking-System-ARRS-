from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from jobs.models import JobDescription
from resumes.models import Resume
from .models import Ranking
from .utils import calculate_similarity, extract_skills

@api_view(['GET'])
def test_ranking(request):
    return Response({"message": "Ranking app is working successfully!"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rank_resumes(request, job_id):
    """Rank all resumes for a given job"""
    try:
        job = JobDescription.objects.get(id=job_id)
    except JobDescription.DoesNotExist:
        return Response({"error": "Job not found"}, status=404)

    resumes = Resume.objects.filter(job=job)
    if not resumes.exists():
        return Response({"message": "No resumes uploaded for this job."})

    rankings = []
    for resume in resumes:
        sim_score = calculate_similarity(job.description, resume.parsed_text or "")
        skills = extract_skills(resume.parsed_text or "")
        ranking = Ranking.objects.create(
            job=job,
            resume=resume,
            similarity_score=sim_score,
            matched_skills=skills,
            rank_score=sim_score * 100  # normalize to %
        )
        rankings.append(ranking)

    # Sort by score
    rankings.sort(key=lambda r: r.rank_score, reverse=True)
    for i, rank in enumerate(rankings, start=1):
        rank.rank_position = i
        rank.save()

    return Response({
        "job": job.title,
        "rankings": [
            {
                "candidate": r.resume.user.username,
                "score": r.rank_score,
                "skills": r.matched_skills,
                "rank": r.rank_position
            } for r in rankings
        ]
    })
