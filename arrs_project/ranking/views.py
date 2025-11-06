from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from jobs.models import JobDescription
from resumes.models import Resume
from .models import Ranking
from .utils import batch_rank_resumes


@api_view(['GET'])
def test_ranking(request):
    return Response({"message": " Ranking app is working successfully!"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rank_resumes(request, job_id):
    """Rank all resumes for a given job using the AI-powered scoring system."""
    try:
        job = JobDescription.objects.get(id=job_id)
        resumes = Resume.objects.all()

        # Prepare resumes with extracted text
        resumes_data = [
            {'id': r.id, 'name': r.user.username, 'text': r.parsed_text}
            for r in resumes if r.parsed_text
        ]

        if not resumes_data:
            return Response({'error': 'No resumes found with parsed text.'}, status=status.HTTP_404_NOT_FOUND)

        # Run AI ranking
        ranked = batch_rank_resumes(job.description, resumes_data, job.experience_required)

        # Clear old rankings for this job (optional, to keep DB clean)
        Ranking.objects.filter(job=job).delete()

        # Save the new results to the Ranking table
        for res in ranked:
            details = res['details']
            Ranking.objects.create(
                job=job,
                resume=Resume.objects.get(id=res['resume_id']),
                similarity_score=details['semantic_similarity'],
                skill_match_score=details['skill_match'],
                keyword_density_score=details['keyword_density'],
                experience_score=details['experience_score'],
                education_score=details['education_score'],
                final_score=details['final_score'],
                matched_skills=details['matched_skills'],
                missing_skills=details['missing_skills'],
                resume_skills=details['resume_skills'],
                rank_position=res['rank']
            )

        # Return the ranked list
        return Response({
            'job_id': job.id,
            'job_title': job.title,
            'ranked_resumes': ranked,
            'message': ' AI resume ranking completed successfully.'
        }, status=status.HTTP_200_OK)

    except JobDescription.DoesNotExist:
        return Response({'error': 'Job not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(" Ranking error:", e)
        return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ranked_results(request, job_id):
    rankings = Ranking.objects.filter(job_id=job_id).order_by('rank_position')
    if not rankings.exists():
        return Response({'message': 'No rankings found for this job.'}, status=status.HTTP_404_NOT_FOUND)

    data = [
        {
            'candidate': r.resume.user.username,
            'score': r.final_score,
            'rank': r.rank_position,
            'matched_skills': r.matched_skills,
            'missing_skills': r.missing_skills,
            'details': {
                'semantic_similarity': r.similarity_score,
                'skill_match': r.skill_match_score,
                'keyword_density': r.keyword_density_score,
                'experience_score': r.experience_score,
                'education_score': r.education_score
            }
        }
        for r in rankings
    ]
    return Response({'job_id': job_id, 'results': data}, status=status.HTTP_200_OK)
