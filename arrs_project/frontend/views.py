from django.shortcuts import render, redirect
from jobs.models import JobDescription
from resumes.models import Resume
from ranking.models import Ranking
import requests
from django.contrib.auth.decorators import login_required
from ranking.utils import calculate_similarity, extract_skills
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.contrib.auth.models import User
from users.models import User as CustomUser  
from django.contrib import messages



def home(request):
    return render(request, 'home.html')

def job_list(request):
    jobs = JobDescription.objects.all()
    return render(request, 'job_list.html', {'jobs': jobs})

def upload_resume(request):
    jobs = JobDescription.objects.all()
    message = None

    if request.method == 'POST':
        job_id = request.POST.get('job')
        file = request.FILES.get('file')
        if job_id and file:
            Resume.objects.create(user=request.user, job_id=job_id, file=file)
            message = " Resume uploaded successfully!"
        else:
            message = " Please select a job and upload a file."
    return render(request, 'upload_resume.html', {'jobs': jobs, 'message': message})

def ranking_results(request, job_id):
    job = JobDescription.objects.get(id=job_id)
    rankings = Ranking.objects.filter(job=job).order_by('rank_position')
    return render(request, 'ranking_results.html', {'job': job, 'rankings': rankings})


@login_required
def recruiter_dashboard(request):
    """Recruiter dashboard to create and list jobs"""
    message = None

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        required_skills = request.POST.get('required_skills')
        experience_required = request.POST.get('experience_required')

        if title and description:
            JobDescription.objects.create(
                recruiter=request.user,
                title=title,
                description=description,
                required_skills=required_skills,
                experience_required=experience_required
            )
            message = "✅ Job created successfully!"
        else:
            message = "⚠️ Please fill all required fields."

    jobs = JobDescription.objects.filter(recruiter=request.user).order_by('-created_at')
    return render(request, 'recruiter_dashboard.html', {'jobs': jobs, 'message': message})


@login_required
def trigger_ranking(request, job_id):
    """Trigger AI resume ranking from dashboard"""
    from jobs.models import JobDescription
    from resumes.models import Resume
    from ranking.models import Ranking

    try:
        job = JobDescription.objects.get(id=job_id, recruiter=request.user)
    except JobDescription.DoesNotExist:
        return render(request, 'recruiter_dashboard.html', {'message': '❌ Job not found.'})

    resumes = Resume.objects.filter(job=job)
    if not resumes.exists():
        return render(request, 'recruiter_dashboard.html', {'message': '⚠️ No resumes uploaded yet for this job.'})

    # Clear previous rankings
    Ranking.objects.filter(job=job).delete()

    # Compute new rankings
    rankings = []
    for resume in resumes:
        sim_score = calculate_similarity(job.description, resume.parsed_text or "")
        skills = extract_skills(resume.parsed_text or "")
        ranking = Ranking.objects.create(
            job=job,
            resume=resume,
            similarity_score=sim_score,
            matched_skills=skills,
            rank_score=sim_score * 100
        )
        rankings.append(ranking)

    rankings.sort(key=lambda r: r.rank_score, reverse=True)
    for i, rank in enumerate(rankings, start=1):
        rank.rank_position = i
        rank.save()

    message = f"🤖 AI Ranking complete for job '{job.title}'."
    jobs = JobDescription.objects.filter(recruiter=request.user)
    return render(request, 'recruiter_dashboard.html', {'jobs': jobs, 'message': message})


def login_view(request):
    """Handles user login for recruiters and jobseekers."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on role
            if user.role == 'recruiter':
                return redirect('/dashboard/')
            else:
                return redirect('/jobs/')
        else:
            return render(request, 'login.html', {'message': ' Invalid username or password.'})

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def register_view(request):
    """Handles new user registration for Recruiter or Jobseeker."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')

        if not username or not email or not password or not role:
            return render(request, 'register.html', {'message': ' Please fill all required fields.'})

        if password != confirm_password:
            return render(request, 'register.html', {'message': ' Passwords do not match.'})

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'register.html', {'message': ' Username already taken.'})

        # Create user
        user = CustomUser.objects.create_user(username=username, email=email, password=password, role=role)
        messages.success(request, " Account created successfully! Please login.")
        return redirect('/login/')

    return render(request, 'register.html')
