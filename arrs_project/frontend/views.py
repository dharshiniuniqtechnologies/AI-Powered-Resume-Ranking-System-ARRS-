from django.shortcuts import get_object_or_404, render, redirect
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

@login_required
def profile_view(request):
    """Show and update user profile."""
    message = None
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        if username and email:
            request.user.username = username
            request.user.email = email
            request.user.save()
            message = " Profile updated successfully!"
        else:
            message = " Both fields are required."

    resumes = Resume.objects.filter(user=request.user)
    return render(request, "profile.html", {"resumes": resumes, "message": message})


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



@login_required(login_url='/login/')
def recruiter_dashboard(request):
    """Recruiter dashboard – accessible only to logged-in recruiters."""
    
    # Optional: ensure user is a recruiter
    # if not hasattr(request.user, 'is_recruiter') or not request.user.is_recruiter:
    #     return render(request, '403.html', status=403)

    # Fetch only this recruiter's jobs
    jobs = JobDescription.objects.filter(recruiter=request.user)
    selected_job = request.GET.get('job_id')
    ranked_results = []

    if selected_job:
        rankings = Ranking.objects.filter(job_id=selected_job).order_by('rank_position')
        if rankings.exists():
            ranked_results = [
                {
                    'rank': r.rank_position,
                    'name': r.resume.user.username,
                    'score': r.final_score,
                    'details': {
                        'semantic_similarity': round(r.similarity_score, 2),
                        'skill_match': round(r.skill_match_score, 2),
                        'keyword_density': round(r.keyword_density_score, 2),
                        'experience_score': round(r.experience_score, 2),
                        'education_score': round(r.education_score, 2),
                        'matched_skills': r.matched_skills,
                        'missing_skills': r.missing_skills,
                        'resume_skills': r.resume_skills,
                    }
                }
                for r in rankings
            ]

    return render(request, 'recruiter_dashboard.html', {
        'jobs': jobs,
        'ranked_results': ranked_results,
        'selected_job': selected_job
    })


@login_required
def create_job(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        skills = request.POST.get('required_skills')
        experience = request.POST.get('experience_required')

        JobDescription.objects.create(
            title=title,
            description=description,
            required_skills=skills,
            experience_required=experience,
            recruiter=request.user  # ✅ set recruiter here
        )
        return redirect('recruiter-dashboard')

    return render(request, 'create_job.html')

@login_required
def edit_job(request, job_id):
    """Allow recruiter to edit an existing job"""
    job = get_object_or_404(JobDescription, id=job_id, recruiter=request.user)

    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.description = request.POST.get('description')
        job.required_skills = request.POST.get('required_skills')
        job.experience_required = request.POST.get('experience_required')
        job.save()

        messages.success(request, "✅ Job updated successfully!")
        return redirect('recruiter-dashboard')

    return render(request, 'edit_job.html', {'job': job})


@login_required
def delete_job(request, job_id):
    """Allow recruiter to delete a job"""
    job = get_object_or_404(JobDescription, id=job_id, recruiter=request.user)
    job.delete()
    messages.success(request, "🗑️ Job deleted successfully!")
    return redirect('recruiter-dashboard')


@login_required
def trigger_ranking(request, job_id):
    """Trigger AI resume ranking from dashboard"""
    
    try:
        job = JobDescription.objects.get(id=job_id, recruiter=request.user)
    except JobDescription.DoesNotExist:
        return render(request, 'recruiter_dashboard.html', {'message': ' Job not found.'})

    resumes = Resume.objects.filter(job=job)
    if not resumes.exists():
        return render(request, 'recruiter_dashboard.html', {'message': ' No resumes uploaded yet for this job.'})

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

    message = f" AI Ranking complete for job '{job.title}'."
    jobs = JobDescription.objects.filter(recruiter=request.user)
    return render(request, 'recruiter_dashboard.html', {'jobs': jobs, 'message': message})


