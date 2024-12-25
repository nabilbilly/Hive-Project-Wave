from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class AdminRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            # List of paths that should redirect admins to admin dashboard
            user_only_paths = [
                '/dashboard/',
                '/job-view/',
                '/profile/',
                '/ExploreInterest/',
                '/Experted-Earn/',
            ]
            
            current_path = request.path.lstrip('/')
            
            # Check if current path starts with any user-only path
            if any(request.path.startswith(path) for path in user_only_paths):
                messages.info(request, 'Admin users should use the admin dashboard.')
                return redirect('admin:index')

        response = self.get_response(request)
        return response
