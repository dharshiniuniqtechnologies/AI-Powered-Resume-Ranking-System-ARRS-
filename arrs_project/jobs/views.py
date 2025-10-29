from rest_framework import viewsets, permissions
from .models import JobDescription
from .serializers import JobSerializer

class JobViewSet(viewsets.ModelViewSet):
    queryset = JobDescription.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]
