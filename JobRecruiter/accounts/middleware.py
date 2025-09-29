from django.shortcuts import redirect
from django.urls import reverse
from .models import Profile

class ProfileCompletionMiddleware:
    """
    Ensures that a logged-in user is redirected to the account selection page
    if they have not yet created a Profile.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # The code is executed on each request
        response = self.get_response(request)

        # Check if the user is authenticated and not an admin
        if request.user.is_authenticated and not request.user.is_staff:
            # Check if the user has a main Profile object
            # The 'hasattr()' check prevents an error if the profile doesn't exist
            if not hasattr(request.user, 'profile'):
                # Allow access to the account selection page and logout page
                allowed_paths = [reverse('accounts.account_select'), reverse('accounts.logout')]
                if request.path not in allowed_paths:
                    return redirect('accounts.account_select')

        return response
    
class ProfileMiddleware:
    """
    Attaches the user's profile to the request object so it can be
    accessed in any template.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                request.profile = Profile.objects.get(user=request.user)
            except Profile.DoesNotExist:
                request.profile = None
        else:
            request.profile = None
        
        response = self.get_response(request)
        return response