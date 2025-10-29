from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Resume
from .serializers import ResumeSerializer
import fitz  # PyMuPDF

class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Auto-parse text from PDF when resume is uploaded"""
        resume = serializer.save()
        file_path = resume.file.path
        text = ""

        try:
            with fitz.open(file_path) as pdf:
                for page in pdf:
                    text += page.get_text("text")
        except Exception as e:
            print("Error parsing resume:", e)

        resume.parsed_text = text
        resume.save()

    @action(detail=False, methods=['get'])
    def my_resumes(self, request):
        """Fetch all resumes uploaded by the logged-in user"""
        resumes = Resume.objects.filter(user=request.user)
        serializer = self.get_serializer(resumes, many=True)
        return Response(serializer.data)
