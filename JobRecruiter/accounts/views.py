from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

# --- Import our new forms and models ---
from .forms import CustomUserCreationForm, CustomErrorList, JobSeekerProfileForm, EmployerProfileForm
from .models import Profile, JobSeekerProfile, EmployerProfile

# --- User Authentication Views ---

def signup_view(request):
    """
    Handles user registration using the custom form.
    On success, it logs the user in and redirects, letting the middleware
    send them to the account selection page.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            user = form.save()
            auth_login(request, user) # Log the user in automatically
            return redirect('accounts.account_select') # Redirect to choose account type
    else:
        form = CustomUserCreationForm(error_class=CustomErrorList)
    
    return render(request, 'accounts/signup.html', {'form': form, 'title': 'Sign Up'})

def login_view(request):
    """
    Handles user login.
    """
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            auth_login(request, user)
            return redirect('home.index') # Redirect to home, middleware will intercept if needed
        else:
            messages.error(request, 'The username or password was incorrect.')
            return render(request, 'accounts/login.html', {'title': 'Login'})
    
    return render(request, 'accounts/login.html', {'title': 'Login'})

@login_required
def logout_view(request):
    """
    Logs the user out.
    """
    auth_logout(request)
    return redirect('home.index')

# --- Profile Creation and Management Views ---

@login_required
def select_account_view(request):
    """
    Allows a new user to select their account type (Job Seeker or Employer).
    This view creates the main Profile object.
    """
    if hasattr(request.user, 'profile'):
        return redirect('accounts.profile') # If profile exists, go to their profile

    if request.method == 'POST':
        account_type = request.POST.get('account_type')
        if account_type in ['jobseeker', 'employer']:
            profile = Profile.objects.create(user=request.user, account_type=account_type)
            if account_type == 'jobseeker':
                return redirect('accounts.create_jobseeker_profile')
            else:
                return redirect('accounts.create_employer_profile')

    return render(request, 'accounts/account_select.html')

@login_required
def create_jobseeker_profile_view(request):
    """
    Handles the creation of a detailed JobSeekerProfile using a form.
    """
    profile = get_object_or_404(Profile, user=request.user)
    if profile.account_type != 'jobseeker':
        return redirect('home.index') # Or show an error

    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            jobseeker_profile = form.save(commit=False)
            jobseeker_profile.profile = profile
            jobseeker_profile.save()
            messages.success(request, 'Your Job Seeker profile has been created!')
            return redirect('accounts.profile')
    else:
        form = JobSeekerProfileForm()

    return render(request, 'accounts/profile_form.html', {'form': form, 'title': 'Create Your Job Seeker Profile'})

@login_required
def create_employer_profile_view(request):
    """
    Handles the creation of a detailed EmployerProfile using a form.
    """
    profile = get_object_or_404(Profile, user=request.user)
    if profile.account_type != 'employer':
        return redirect('home.index') # Or show an error

    if request.method == 'POST':
        form = EmployerProfileForm(request.POST)
        if form.is_valid():
            employer_profile = form.save(commit=False)
            employer_profile.profile = profile
            employer_profile.save()
            messages.success(request, 'Your Employer profile has been created!')
            return redirect('accounts.profile')
    else:
        form = EmployerProfileForm()
        
    return render(request, 'accounts/profile_form.html', {'form': form, 'title': 'Create Your Employer Profile'})

@login_required
def profile_view(request):
    """
    Displays the correct profile (Job Seeker or Employer) based on the user's
    account type. This replaces your original 'profile' view.
    """
    profile = get_object_or_404(Profile, user=request.user)
    
    if profile.account_type == 'jobseeker':
        # Use a try-except block in case the detailed profile hasn't been created yet
        try:
            detailed_profile = profile.jobseekerprofile
            return render(request, 'accounts/jobseeker_profile.html', {'profile': detailed_profile})
        except JobSeekerProfile.DoesNotExist:
            return redirect('accounts.create_jobseeker_profile')

    elif profile.account_type == 'employer':
        try:
            detailed_profile = profile.employerprofile
            return render(request, 'accounts/employer_profile.html', {'profile': detailed_profile})
        except EmployerProfile.DoesNotExist:
            return redirect('accounts.create_employer_profile')
    
    # Fallback in case something is wrong with the account type
    return redirect('home.index')

@login_required
def edit_profile_view(request):
    """
    Allows a user to edit their profile. It serves the correct form based on
    the user's account type. This replaces your original 'edit_profile' view.
    """
    profile = get_object_or_404(Profile, user=request.user)

    if profile.account_type == 'jobseeker':
        detailed_profile = get_object_or_404(JobSeekerProfile, profile=profile)
        form_class = JobSeekerProfileForm
        template_name = 'accounts/profile_form.html'
    elif profile.account_type == 'employer':
        detailed_profile = get_object_or_404(EmployerProfile, profile=profile)
        form_class = EmployerProfileForm
        template_name = 'accounts/profile_form.html'
    else:
        return redirect('home.index')

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=detailed_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts.profile')
    else:
        form = form_class(instance=detailed_profile)

    return render(request, template_name, {'form': form, 'title': 'Edit Your Profile'})

@login_required
def public_profile_view(request, user_id):
    """
    Displays a specific job seeker's public profile.
    This view is intended to be used by employers.
    """
    # Security Check: Ensure the person viewing is an employer
    if not request.user.profile or request.user.profile.account_type != 'employer':
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home.index')

    # Get the job seeker's User object
    job_seeker_user = get_object_or_404(User, id=user_id)
    
    try:
        # Get the detailed profile from that User
        detailed_profile = job_seeker_user.profile.jobseekerprofile
        back_url = request.META.get('HTTP_REFERER')
        # We can re-use your existing template for a job seeker profile
        return render(request, 'accounts/jobseeker_profile.html', {
            'profile': detailed_profile,
            'is_public_view': True, # Optional: lets template know this isn't the user's own profile
            'back_url': back_url
        })
    
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, "This user does not have a job seeker profile.")
        # Go back to the page they came from (the applicants list)
        return redirect(request.META.get('HTTP_REFERER', 'jobpostings:my_posted_jobs'))
    
    except Profile.DoesNotExist:
        messages.error(request, "This user does not have a base profile.")
        return redirect(request.META.get('HTTP_REFERER', 'jobpostings:my_posted_jobs'))