from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import JobListing, JobApplication, JobReport, JobSearchPreferences, UserJobProfile
from Accounts.models import Skill, UserProfile
from TalentMatching.services import TalentMatchingService

# Create your views here.
@login_required(login_url='accounts:Login')
def job_view(request):
    # Initialize the talent matching service
    matching_service = TalentMatchingService()
    
    # Get search parameters
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    experience = request.GET.get('experience', '')
    
    # Base queryset
    jobs = JobListing.objects.filter(is_active=True)
    
    # Apply filters
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(description__icontains=query)
        )
    
    if location:
        jobs = jobs.filter(location__icontains=location)
        
    if experience:
        jobs = jobs.filter(experience_level__icontains=experience)
    
    # Get recommended jobs based on user's profile
    recommended_jobs = []
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        # Compute or update user's vector
        matching_service.compute_candidate_vector(request.user)
        # Find matching jobs
        matches = matching_service.find_matches_for_candidate(request.user, min_score=0.5, limit=5)
        recommended_jobs = [match['job'] for match in matches]
    except UserProfile.DoesNotExist:
        pass
    
    # Get user's applications
    applications = JobApplication.objects.filter(user=request.user).values_list('job_id', flat=True)
    
    context = {
        'jobs': jobs,
        'recommended_jobs': recommended_jobs,
        'applied_jobs': applications,
        'query': query,
        'location': location,
        'experience': experience,
    }
    
    return render(request, 'Job/jobpage.html', context)

@login_required(login_url='accounts:Login')
def dashboard_home(request):
    # Get user's job applications
    applications = JobApplication.objects.filter(user=request.user).order_by('-applied_at')
    
    # Get recommended jobs based on user's skills and preferences
    user_preferences = JobSearchPreferences.objects.get_or_create(user=request.user)[0]
    recommended_jobs = JobListing.objects.filter(
        is_active=True,
        salary_min__gte=user_preferences.min_salary,
        salary_max__lte=user_preferences.max_salary
    ).order_by('-created_at')[:5]
    
    context = {
        'applications': applications,
        'recommended_jobs': recommended_jobs,
    }
    return render(request, 'Job/dashboard_home.html', context)

@login_required(login_url='accounts:Login')
def job_search(request):
    query = request.GET.get('q', '')
    job_type = request.GET.get('type', '')
    location = request.GET.get('location', '')
    
    jobs = JobListing.objects.filter(is_active=True)
    
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(description__icontains=query)
        )
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
        
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    context = {
        'jobs': jobs,
        'query': query,
        'job_type': job_type,
        'location': location,
    }
    return render(request, 'Job/job_search.html', context)

@login_required(login_url='accounts:Login')
def job_detail(request, job_id):
    job = get_object_or_404(JobListing, id=job_id, is_active=True)
    has_applied = JobApplication.objects.filter(user=request.user, job=job).exists()
    
    context = {
        'job': job,
        'has_applied': has_applied,
    }
    return render(request, 'Job/job_detail.html', context)

@login_required(login_url='accounts:Login')
def apply_job(request, job_id):
    if request.method == 'POST':
        job = get_object_or_404(JobListing, id=job_id, is_active=True)
        
        # Check if already applied
        if JobApplication.objects.filter(user=request.user, job=job).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'You have already applied for this job.'
            })
        
        # Create application
        JobApplication.objects.create(user=request.user, job=job)
        
        # Update job vector after new application
        matching_service = TalentMatchingService()
        matching_service.compute_job_vector(job)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Application submitted successfully!'
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    })

@login_required(login_url='accounts:Login')
def my_applications(request):
    applications = JobApplication.objects.filter(user=request.user).order_by('-applied_at')
    
    context = {
        'applications': applications,
    }
    return render(request, 'Job/my_applications.html', context)

@login_required(login_url='accounts:Login')
def update_preferences(request):
    if request.method == 'POST':
        preferences = JobSearchPreferences.objects.get_or_create(user=request.user)[0]
        preferences.min_salary = request.POST.get('min_salary', 0)
        preferences.max_salary = request.POST.get('max_salary', 100000)
        preferences.save()
        
        messages.success(request, 'Preferences updated successfully!')
        return redirect('dashboard_home')
    
    preferences = JobSearchPreferences.objects.get_or_create(user=request.user)[0]
    context = {
        'preferences': preferences,
    }
    return render(request, 'Job/update_preferences.html', context)

@login_required(login_url='accounts:Login')
def report_job(request, job_id):
    if request.method == 'POST':
        job = get_object_or_404(JobListing, id=job_id)
        reason = request.POST.get('reason')
        additional_info = request.POST.get('additional_info', '')
        
        JobReport.objects.create(
            user=request.user,
            job=job,
            reason=reason,
            additional_info=additional_info
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Job reported successfully. Our team will review it.'
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    })

@login_required
def job_introduction(request):
    if request.method == 'POST':
        # Get form data
        employment_type = request.POST.get('employment_type')
        english_level = request.POST.get('english_level')
        expected_salary = request.POST.get('expected_salary')
        interests = request.POST.get('interests')
        years_of_experience = request.POST.get('years_of_experience')
        education_level = request.POST.get('education_level')
        preferred_location = request.POST.get('preferred_location')
        work_schedule = request.POST.get('work_schedule')
        email_notifications = request.POST.get('email_notifications', True)
        skills = request.POST.getlist('skills')

        # Create or update user job profile
        profile, created = UserJobProfile.objects.get_or_create(user=request.user)
        profile.employment_type = employment_type
        profile.english_level = english_level
        profile.expected_salary = expected_salary
        profile.interests = interests
        profile.years_of_experience = years_of_experience
        profile.education_level = education_level
        profile.preferred_location = preferred_location
        profile.work_schedule = work_schedule
        profile.email_notifications = email_notifications
        profile.save()

        # Add skills
        profile.skills.clear()
        for skill_name in skills:
            skill, _ = Skill.objects.get_or_create(name=skill_name)
            profile.skills.add(skill)

        return JsonResponse({'status': 'success'})

    # GET request - render appropriate introduction step
    step = request.GET.get('step', 'employment')
    template_map = {
        'employment': 'Introduction/EmploymentOption.html',
        'english': 'Introduction/EnglishLevel.html',
        'salary': 'Introduction/ExpertedEarn.html',
        'interests': 'Introduction/Exploreinterest.html',
        'experience': 'Introduction/JobExperience.html',
        'education': 'Introduction/LevelOfEducation.html',
        'location': 'Introduction/LocationOfWork.html',
        'schedule': 'Introduction/WorkSchedule.html',
        'notifications': 'Introduction/EmailNotification.html',
    }

    return render(request, template_map.get(step, 'Introduction/introduction.html'))

@login_required
def save_introduction_step(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    step = request.POST.get('step')
    profile, created = UserJobProfile.objects.get_or_create(user=request.user)

    if step == 'employment':
        profile.employment_type = request.POST.get('employment_type')
    elif step == 'english':
        profile.english_level = request.POST.get('english_level')
    elif step == 'salary':
        profile.expected_salary = request.POST.get('expected_salary')
    elif step == 'interests':
        profile.interests = request.POST.get('interests')
    elif step == 'experience':
        profile.years_of_experience = request.POST.get('years_of_experience')
    elif step == 'education':
        profile.education_level = request.POST.get('education_level')
    elif step == 'location':
        profile.preferred_location = request.POST.get('preferred_location')
    elif step == 'schedule':
        profile.work_schedule = request.POST.get('work_schedule')
    elif step == 'notifications':
        profile.email_notifications = request.POST.get('email_notifications', True)

    profile.save()
    return JsonResponse({'status': 'success', 'next_step': get_next_step(step)})

def get_next_step(current_step):
    steps = ['employment', 'english', 'salary', 'interests', 'experience', 
             'education', 'location', 'schedule', 'notifications']
    try:
        current_index = steps.index(current_step)
        if current_index < len(steps) - 1:
            return steps[current_index + 1]
        return 'complete'
    except ValueError:
        return 'employment'
