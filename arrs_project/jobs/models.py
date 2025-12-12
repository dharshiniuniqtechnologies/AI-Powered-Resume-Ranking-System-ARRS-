from django.db import models
from users.models import User

class JobDescription(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.TextField()
    experience_required = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
