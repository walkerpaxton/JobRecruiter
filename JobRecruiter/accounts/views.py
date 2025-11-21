from django.db.models import Q
from .forms import CandidateSearchForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

# --- Import our new forms and models ---
from .forms import CustomUserCreationForm, CustomErrorList, JobSeekerProfileForm, EmployerProfileForm, UserEmailForm
from .models import Profile, JobSeekerProfile, EmployerProfile, SavedSearch

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


@login_required
def add_email_view(request):
    """
    Allows users without email addresses to add one.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            # Check if email is already taken
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.error(request, "This email address is already in use.")
            else:
                request.user.email = email
                request.user.save()
                messages.success(request, "Email address added successfully!")
                return redirect('accounts.profile')
        else:
            messages.error(request, "Please enter a valid email address.")
    
    return render(request, 'accounts/add_email.html', {'title': 'Add Email Address'})

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

    # Handle email form separately
    email_form = UserEmailForm(instance=request.user)

    if request.method == 'POST':
        # Check if it's email form submission
        if 'email_submit' in request.POST:
            email_form = UserEmailForm(request.POST, instance=request.user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, 'Email address updated successfully!')
                return redirect('accounts.create_jobseeker_profile')
        else:
            # Handle profile form submission
            form = JobSeekerProfileForm(request.POST, request.FILES)
            if form.is_valid():
                jobseeker_profile = form.save(commit=False)
                jobseeker_profile.profile = profile
                jobseeker_profile.save()
                messages.success(request, 'Your Job Seeker profile has been created!')
                return redirect('accounts.profile')
    else:
        form = JobSeekerProfileForm()

    return render(request, 'accounts/profile_form.html', {
        'form': form, 
        'email_form': email_form,
        'title': 'Create Your Job Seeker Profile'
    })

@login_required
def create_employer_profile_view(request):
    """
    Handles the creation of a detailed EmployerProfile using a form.
    """
    profile = get_object_or_404(Profile, user=request.user)
    if profile.account_type != 'employer':
        return redirect('home.index') # Or show an error

    # Handle email form separately
    email_form = UserEmailForm(instance=request.user)
    
    if request.method == 'POST':
        # Check if it's email form submission
        if 'email_submit' in request.POST:
            email_form = UserEmailForm(request.POST, instance=request.user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, 'Email address updated successfully!')
                return redirect('accounts.create_employer_profile')
        else:
            # Handle profile form submission
            form = EmployerProfileForm(request.POST)
            if form.is_valid():
                employer_profile = form.save(commit=False)
                employer_profile.profile = profile
                employer_profile.save()
                messages.success(request, 'Your Employer profile has been created!')
                return redirect('accounts.profile')
    else:
        form = EmployerProfileForm()
        
    return render(request, 'accounts/profile_form.html', {
        'form': form, 
        'email_form': email_form,
        'title': 'Create Your Employer Profile'
    })

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

    # Handle email form separately
    email_form = UserEmailForm(instance=request.user)
    
    if request.method == 'POST':
        # Check if it's email form submission
        if 'email_submit' in request.POST:
            email_form = UserEmailForm(request.POST, instance=request.user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, 'Email address updated successfully!')
                return redirect('accounts.edit_profile')
        else:
            # Handle profile form submission
            form = form_class(request.POST, request.FILES, instance=detailed_profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts.profile')
    else:
        form = form_class(instance=detailed_profile)

    return render(request, template_name, {
        'form': form, 
        'email_form': email_form,
        'title': 'Edit Your Profile'
    })

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
    

@login_required
def search_candidates_view(request):
    """
    Allows employers to search for candidates based on location and keywords
    (skills, summary, etc).
    """
    # Security Check: Only Employers allowed
    if not hasattr(request.user, 'profile') or request.user.profile.account_type != 'employer':
        messages.error(request, "Only employers can search for candidates.")
        return redirect('home.index')

    form = CandidateSearchForm(request.GET or None)
    results = []

    # We try/except to handle cases where the profile might be incomplete, though unlikely
    try:
        employer_profile = request.user.profile.employerprofile
        saved_searches = SavedSearch.objects.filter(recruiter=employer_profile).order_by('-created_at')
    except:
        saved_searches = []

    # Only run query if the form has data (user clicked Search)
    if request.GET and form.is_valid():
        location_query = form.cleaned_data.get('location')
        keywords_query = form.cleaned_data.get('keywords')

        if form.cleaned_data.get('save_search'):
            search_name = form.cleaned_data.get('search_name') or "Untitled Search"
            
            # Create the saved search record
            SavedSearch.objects.create(
                recruiter=request.user.profile.employerprofile,
                name=search_name,
                location=location_query,
                keywords=keywords_query
            )
            messages.success(request, f"Search '{search_name}' has been saved!")

        # Start with all job seekers
        candidates = JobSeekerProfile.objects.all()

        if location_query:
            candidates = candidates.filter(location__icontains=location_query)

        if keywords_query:
            # Search in technical skills, soft skills, and summary
            candidates = candidates.filter(
                Q(technical_skills__icontains=keywords_query) | 
                Q(soft_skills__icontains=keywords_query) |
                Q(summary__icontains=keywords_query)
            ).distinct()

        results = candidates

    return render(request, 'accounts/candidate_search.html', {
        'form': form,
        'results': results,
        'saved_searches': saved_searches,
        'title': 'Search Candidates'
    })

@login_required
def delete_saved_search_view(request, pk):
    """
    Deletes a specific saved search.
    """
    # Security: Ensure the saved search exists AND belongs to the current logged-in employer
    saved_search = get_object_or_404(SavedSearch, pk=pk, recruiter__profile__user=request.user)
    
    saved_search.delete()
    messages.success(request, "Saved search deleted successfully.")
    return redirect('search_candidates')

@login_required
def edit_saved_search_view(request, pk):
    """
    Allows editing the Name, Location, and Keywords of a saved search.
    """
    # Security: Ensure ownership
    saved_search = get_object_or_404(SavedSearch, pk=pk, recruiter__profile__user=request.user)
    
    if request.method == 'POST':
        # Manually process the update to keep it simple without a ModelForm
        new_name = request.POST.get('search_name')
        new_location = request.POST.get('location')
        new_keywords = request.POST.get('keywords')
        
        if new_name:
            saved_search.name = new_name
            saved_search.location = new_location
            saved_search.keywords = new_keywords
            saved_search.save()
            messages.success(request, "Saved search updated successfully.")
            return redirect('search_candidates')
        else:
            messages.error(request, "Search name is required.")

    return render(request, 'accounts/edit_saved_search.html', {
        'saved_search': saved_search
    })