from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse
from .services import TalentMatchingService
from .models import MatchPreference
from DashboardPages.models import JobListing
import json
import logging

logger = logging.getLogger(__name__)
matching_service = TalentMatchingService()

@login_required(login_url='accounts:Login')
def matching_dashboard(request):
    """Dashboard showing job matches for the logged-in user"""
    try:
        # Get or compute candidate vector
        matching_service.compute_candidate_vector(request.user)
        
        # Find matches
        matches = matching_service.find_matches_for_candidate(request.user)
        
        # Get user preferences
        preferences, created = MatchPreference.objects.get_or_create(user=request.user)
        
        context = {
            'matches': matches,
            'preferences': preferences
        }
        
        return render(request, 'TalentMatching/dashboard.html', context)
    except Exception as e:
        logger.error(f"Error in matching dashboard for user {request.user.username}: {str(e)}")
        return render(request, 'TalentMatching/error.html', {'error': str(e)})

@login_required(login_url='accounts:Login')
@require_http_methods(["POST"])
def update_preferences(request):
    """Update user's matching preferences"""
    try:
        data = json.loads(request.body)
        preferences, created = MatchPreference.objects.get_or_create(user=request.user)
        
        # Update fields
        preferences.min_salary = data.get('min_salary', preferences.min_salary)
        preferences.max_salary = data.get('max_salary', preferences.max_salary)
        preferences.preferred_locations = data.get('preferred_locations', preferences.preferred_locations)
        preferences.remote_only = data.get('remote_only', preferences.remote_only)
        preferences.job_types = data.get('job_types', preferences.job_types)
        preferences.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error updating preferences for user {request.user.username}: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required(login_url='accounts:Login')
def job_matches(request, job_id):
    """View showing candidate matches for a specific job"""
    try:
        job = get_object_or_404(JobListing, id=job_id)
        
        # Ensure user has permission to view matches for this job
        if job.posted_by != request.user:
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
        # Compute job vector if needed
        matching_service.compute_job_vector(job)
        
        # Find matches
        matches = matching_service.find_matches_for_job(job)
        
        context = {
            'job': job,
            'matches': matches
        }
        
        return render(request, 'TalentMatching/job_matches.html', context)
    except Exception as e:
        logger.error(f"Error finding matches for job {job_id}: {str(e)}")
        return render(request, 'TalentMatching/error.html', {'error': str(e)})

@login_required(login_url='accounts:Login')
@require_http_methods(["POST"])
def refresh_matches(request):
    """Manually trigger a refresh of match calculations"""
    try:
        # Recompute vectors
        matching_service.compute_candidate_vector(request.user)
        
        # Find new matches
        matches = matching_service.find_matches_for_candidate(request.user)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Matches refreshed successfully',
            'match_count': len(matches)
        })
    except Exception as e:
        logger.error(f"Error refreshing matches for user {request.user.username}: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
