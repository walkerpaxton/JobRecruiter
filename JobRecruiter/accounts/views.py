from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile
from django.contrib import messages

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})
        
def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET': 
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username = request.POST['username'],
                            password = request.POST['password']
                            )
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html',
                          {'template_data': template_data})
        else: 
            auth_login(request, user)
            return redirect('home.index')
@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

@login_required
def profile(request):
    template_data = {}
    template_data['title'] = 'Profile'
    
    # Get or create profile for the current user
    profile, created = Profile.objects.get_or_create(user=request.user)
    template_data['profile'] = profile
    template_data['is_editing'] = False
    
    return render(request, 'accounts/profile.html', {'template_data': template_data})

@login_required
def edit_profile(request):
    template_data = {}
    template_data['title'] = 'Edit Profile'
    
    # Get or create profile for the current user
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle form submission
        profile.full_name = request.POST.get('full_name', '')
        profile.preferred_name = request.POST.get('preferred_name', '')
        profile.location = request.POST.get('location', '')
        profile.phone = request.POST.get('phone', '')
        profile.linkedin = request.POST.get('linkedin', '')
        profile.summary = request.POST.get('summary', '')
        profile.technical_skills = request.POST.get('technical_skills', '')
        profile.soft_skills = request.POST.get('soft_skills', '')
        profile.degree = request.POST.get('degree', '')
        profile.institution = request.POST.get('institution', '')
        profile.graduation_year = request.POST.get('graduation_year') or None
        profile.gpa = request.POST.get('gpa') or None
        profile.current_job = request.POST.get('current_job', '')
        profile.company = request.POST.get('company', '')
        profile.experience_years = request.POST.get('experience_years', '')
        profile.availability = request.POST.get('availability', '')
        profile.languages = request.POST.get('languages', '')
        profile.certifications = request.POST.get('certifications', '')
        profile.portfolio = request.POST.get('portfolio', '')
        profile.salary_expectation = request.POST.get('salary_expectation', '')
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts.profile')
    
    # Pass profile data to template
    template_data['profile'] = profile
    template_data['is_editing'] = True
    
    return render(request, 'accounts/profile.html', {'template_data': template_data})
