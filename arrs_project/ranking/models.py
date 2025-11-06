from django.db import models
from jobs.models import JobDescription
from resumes.models import Resume

class Ranking(models.Model):
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)

    # Core AI Scores
    similarity_score = models.FloatField(default=0.0)
    skill_match_score = models.FloatField(default=0.0)
    keyword_density_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    education_score = models.FloatField(default=0.0)
    final_score = models.FloatField(default=0.0)

    # Skills and Metadata
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    resume_skills = models.JSONField(default=list)

    rank_position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resume.user.username} - {self.job.title} ({round(self.final_score, 2)})"
