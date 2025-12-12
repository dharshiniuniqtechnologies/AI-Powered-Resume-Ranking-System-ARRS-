from django.db import models
from users.models import User
from jobs.models import JobDescription

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/')
    parsed_text = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"
