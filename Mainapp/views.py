from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from DashboardPages.models import UserIntroduction, InterestCategory
from django.http import JsonResponse
import json

# Create your views here.

def Talentpage(request):
    return render(request,'General/TalentPage.html')

def DevCommunityView(request):
    return render(request, 'General/DevCommunity.html')

def DonatePage(request):
    return render(request, 'Donate/donatepage.html')

def AboutUsPage(request):
    return render(request, 'General/About.html')

def Employerspage(request):
    return render(request, 'General/employers.html')

# introduction Page 

def ExploreInterest(request):
    if request.method == 'POST':
        interests = request.POST.getlist('interests[]')
        if not interests:
            return JsonResponse({'status': 'error', 'message': 'Please select at least one interest'})
            
        if request.user.is_authenticated:
            # Get or create the user's introduction profile
            user_intro, created = UserIntroduction.objects.get_or_create(
                user=request.user,
                defaults={'interests': []}
            )
            
            # Update the interests
            user_intro.interests = interests
            user_intro.save()
            
            # Log the successful update
            print(f"Updated interests for user {request.user.username}: {interests}")
            
            return redirect('Experted-Earn')
        else:
            # For anonymous users, store in session
            request.session['intro_interests'] = interests
            return redirect('Experted-Earn')

    # Get all active categories from the database
    categories = InterestCategory.objects.filter(is_active=True).values_list('name', flat=True)
    
    # If no categories exist in the database, use default categories
    if not categories:
        default_categories = [
            "Data Science and Analytics",
            "Software Development",
            "UI/UX Design",
            "Digital Marketing",
            "Content Writing",
            "Project Management",
            "Customer Service",
            "Sales and Business Development",
            "Virtual Assistant",
            "Graphic Design",
            "Video Editing",
            "Social Media Management",
            "Web Development",
            "Mobile App Development",
            "Quality Assurance"
        ]
        # Create default categories in the database
        for category in default_categories:
            InterestCategory.objects.get_or_create(name=category)
        categories = default_categories

    return render(request, 'Introduction/Exploreinterest.html', {'categories': categories})

def ExpertedEarn(request):
    if request.method == 'POST':
        salary = request.POST.get('salary')
        salary_type = request.POST.get('salary_type')
        if request.user.is_authenticated:
            intro, created = UserIntroduction.objects.get_or_create(user=request.user)
            intro.expected_salary = salary
            intro.salary_type = salary_type
            intro.save()
            return redirect('Years-Of-Experience')
        else:
            request.session['intro_salary'] = salary
            request.session['intro_salary_type'] = salary_type
            return redirect('Years-Of-Experience')

    salary_ranges = {
        'hourly': {'min': 5, 'max': 200, 'step': 5},
        'monthly': {'min': 500, 'max': 20000, 'step': 500},
        'yearly': {'min': 10000, 'max': 200000, 'step': 5000}
    }
    return render(request, 'Introduction/ExpertedEarn.html', {'salary_ranges': salary_ranges})

def YearsOfExperience(request):
    return render(request, 'Introduction/YearsOfExperience.html')

def JobExperience(request):
    return render(request, 'Introduction/JobExperience.html')

def LevelOfEducation(request):
    return render(request, 'Introduction/LevelOfEducation.html')

def EnglishLevel(request):
    return render(request, 'Introduction/EnglishLevel.html')

def LocationOfWork(request):
    return render(request, 'Introduction/LocationOfWork.html')

def EmploymentOption(request):
    return render(request, 'Introduction/EmploymentOption.html')

def JobListType(request):
    return render(request, 'Introduction/JobListType.html')

def WorkSchedule(request):
    return render(request, 'Introduction/WorkSchedule.html')

def TeamSetup(request):
    return render(request, 'Introduction/TeamSetup.html')

def JoinCommunity(request):
    return render(request, 'Introduction/JoinCommunity.html')

def EmailNotification(request):
    return render(request, 'Introduction/EmailNotification.html')