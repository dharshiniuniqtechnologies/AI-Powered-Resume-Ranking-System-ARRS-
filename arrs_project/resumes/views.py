from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Resume
from .serializers import ResumeSerializer
import fitz, os  # PyMuPDF
import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    

    def perform_create(self, serializer):
        """Auto-parse text from uploaded PDF resume with fallback OCR"""
        resume = serializer.save(user=self.request.user)
        file_path = resume.file.path
        text = ""

        print("📁 Uploaded:", file_path)

        # Step 1: Validate extension
        if not file_path.lower().endswith(".pdf"):
            resume.delete()
            raise ValueError("Only PDF files are supported.")

        # Step 2: Try extracting using PyMuPDF
        try:
            with fitz.open(file_path) as pdf:
                for page in pdf:
                    text += page.get_text("text")
        except Exception as e:
            print(f"❌ PyMuPDF parsing failed: {e}")

        # Step 3: Fallback to OCR if text extraction fails
        if len(text.strip()) < 50:
            print("⚠️ PyMuPDF returned little/no text — trying OCR...")
            try:
                pages = convert_from_path(file_path)
                for page_img in pages:
                    ocr_text = pytesseract.image_to_string(page_img)
                    text += ocr_text
                print("✅ OCR extracted text length:", len(text))
            except Exception as e:
                print(f"❌ OCR fallback failed: {e}")
                raise ValueError("Could not extract text from PDF. Please upload a readable resume.")

        if len(text.strip()) == 0:
            raise ValueError("Resume text could not be extracted.")

        resume.parsed_text = text.strip()
        resume.save()
        print("✅ Resume parsed successfully! Text length:", len(text))


        
    def create(self, request, *args, **kwargs):
        """Custom create with user-friendly response messages"""
        try:
            return super().create(request, *args, **kwargs)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Unexpected upload error:", e)
            return Response({"error": "Something went wrong while uploading the resume."},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_resumes(self, request):
        """Fetch all resumes uploaded by the logged-in user"""
        resumes = Resume.objects.filter(user=request.user)
        serializer = self.get_serializer(resumes, many=True)
        return Response(serializer.data)
