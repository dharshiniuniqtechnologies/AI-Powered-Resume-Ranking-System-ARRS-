from django.db import models
from jobs.models import JobDescription
from resumes.models import Resume

class Ranking(models.Model):
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    similarity_score = models.FloatField(default=0.0)
    rank_score = models.FloatField(default=0.0)
    matched_skills = models.JSONField(default=list)
    rank_position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resume.user.username} - {self.job.title} ({self.rank_score})"
