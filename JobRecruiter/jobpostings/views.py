from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from accounts.models import Profile, JobSeekerProfile, EmployerProfile
from .models import JobPosting, Application
from .forms import JobPostingForm, ApplicationForm

US_STATE_NAMES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}


def get_state_full_name(state_value: str) -> str:
    if not state_value:
        return ''
    state_value = state_value.strip()
    if len(state_value) == 2:
        return US_STATE_NAMES.get(state_value.upper(), state_value)
    return state_value

@login_required
def my_posted_jobs(request):
    # 1. Check if the user is an employer
    #    (Using the logic from your base.html)
    if not request.user.profile or request.user.profile.account_type != 'employer':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home.index') # Or wherever you want to send non-employers

    # 2. Get all jobs where 'posted_by' is the current logged-in user
    posted_jobs = JobPosting.objects.filter(posted_by=request.user).order_by('-created_at')
    
    context = {
        'posted_jobs': posted_jobs
    }
    
    # 3. Render the new template we are about to create
    return render(request, 'jobpostings/my_posted_jobs.html', context)

def job_list_view(request):
    jobs = JobPosting.objects.filter(is_active=True)
    search_query = request.GET.get('search', '')
    location_filter = request.GET.get('location', '')
    employment_type_filter = request.GET.get('employment_type', '')
    
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(benefits__icontains=search_query)
        )
    
    if location_filter:
        jobs = jobs.filter(
            Q(city__icontains=location_filter) |
            Q(state__icontains=location_filter) |
            Q(city__icontains=location_filter.split(',')[0].strip()) |
            Q(state__icontains=location_filter.split(',')[1].strip() if ',' in location_filter else '')
        )
    
    if employment_type_filter:
        jobs = jobs.filter(employment_type=employment_type_filter)
    
    context = {
        'jobs': jobs,
        'search_query': search_query,
        'location_filter': location_filter,
        'employment_type_filter': employment_type_filter,
        'employment_types': JobPosting.EMPLOYMENT_TYPE_CHOICES,
    }
    
    return render(request, 'jobpostings/job_list.html', context)


def job_detail_view(request, job_id: int):
    job = get_object_or_404(JobPosting, id=job_id, is_active=True)
    
    # Check if user has already applied to this job
    has_applied = False
    is_jobseeker = False
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job_posting=job, applicant=request.user).exists()
        try:
            profile = Profile.objects.get(user=request.user)
            is_jobseeker = profile.account_type == 'jobseeker'
        except Profile.DoesNotExist:
            is_jobseeker = False
    
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'is_jobseeker': is_jobseeker,
    }
    return render(request, 'jobpostings/job_detail.html', context)


@login_required
def job_create_view(request):
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.account_type != 'employer':
            messages.error(request, 'Only employers can post jobs.')
            return redirect('jobpostings:list')
        employer_profile = EmployerProfile.objects.get(profile=profile)
    except (Profile.DoesNotExist, EmployerProfile.DoesNotExist):
        messages.error(request, 'You must complete your employer profile before posting a job.')
        return redirect('accounts.profile')

    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job: JobPosting = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect(reverse('jobpostings:detail', args=[job.id]))
    else:
        initial_data = {
            'company_name': employer_profile.company_name,
            'city': employer_profile.location.split(',')[0].strip() if ',' in employer_profile.location else employer_profile.location,
            'state': employer_profile.location.split(',')[1].strip() if ',' in employer_profile.location else ''
        }
        form = JobPostingForm(initial=initial_data)

    return render(request, 'jobpostings/job_create.html', {'form': form})

@login_required
def job_edit_view(request, job_id: int):
    job = get_object_or_404(JobPosting, id=job_id, is_active=True)
    if job.posted_by != request.user:
        messages.error(request, 'You are not authorized to edit this job.')
        return redirect('jobpostings:list')
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect(reverse('jobpostings:detail', args=[job.id]))
    else:
        form = JobPostingForm(instance=job)
    
    return render(request, 'jobpostings/edit_job.html', {'form': form, 'job': job})


# In jobpostings/views.py

@login_required
def apply_to_job_view(request, job_id: int):
    job = get_object_or_404(JobPosting, id=job_id, is_active=True)
    
    if not request.profile or request.profile.account_type != 'jobseeker':
        messages.error(request, 'Only job seekers can apply for jobs.')
        return redirect('jobpostings:detail', job_id=job.id)
    
    if Application.objects.filter(job_posting=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied to this job.')
        return redirect('jobpostings:detail', job_id=job.id)
    try:
        jobseeker_profile = request.profile.jobseekerprofile
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, 'Please complete your job seeker profile before applying.')
        # This redirect might need a colon ('accounts:profile') depending on your URL setup.
        return redirect('accounts.profile') 
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            
            application.job_posting = job 
            application.applicant = request.user
            application.save()
            
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('jobpostings:detail', job_id=job.id)
    else:
        form = ApplicationForm()
    
    context = {
        'job': job,
        'form': form,
        'jobseeker_profile': jobseeker_profile,
    }
    
    return render(request, 'jobpostings/apply_to_job.html', context)

@login_required
def job_seeker_applications(request):
    """
    Displays a list of all jobs the current job seeker user has applied to.
    """
    # Ensure the user has a jobseeker profile
    if not request.profile or request.profile.account_type != 'jobseeker':
        return redirect('home.index') # Or some other appropriate page

    applications = Application.objects.filter(applicant=request.user).order_by('-applied_at')
    
    context = {
        'applications': applications
    }
    return render(request, 'jobpostings/jobseekersjobs.html', context)

def job_map_view(request):
    """
    Display an interactive map where users can search for jobs by location.
    """
    # Get search parameters
    search_query = request.GET.get('search', '')
    location_filter = request.GET.get('location', '')
    employment_type_filter = request.GET.get('employment_type', '')
    job_id = request.GET.get('job_id', '')
    
    # Get all active jobs
    jobs = JobPosting.objects.filter(is_active=True)
    
    # Apply filters
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(benefits__icontains=search_query)
        )
    
    if location_filter:
        jobs = jobs.filter(
            Q(city__icontains=location_filter) |
            Q(state__icontains=location_filter) |
            Q(city__icontains=location_filter.split(',')[0].strip()) |
            Q(state__icontains=location_filter.split(',')[1].strip() if ',' in location_filter else '')
        )
    
    if employment_type_filter:
        jobs = jobs.filter(employment_type=employment_type_filter)
    
    # Prepare job data for the map
    job_markers = []
    highlighted_job = None
    for job in jobs:
        # Check if this is the highlighted job
        is_highlighted = job_id and str(job.id) == str(job_id)
        if is_highlighted:
            highlighted_job = job

        display_location = job.full_address()
        state_value = job.state.strip() if job.state else ''
        state_full = get_state_full_name(state_value)
        geocode_parts = [job.address, job.city, state_full or state_value]
        if state_value or state_full:
            geocode_parts.append('USA')
        geocode_query = ", ".join(part for part in geocode_parts if part) or display_location
            
        job_markers.append({
            'id': job.id,
            'title': job.title,
            'company': job.company_name,
            'location': job.location_display(),
            'pay_range': job.pay_range_display(),
            'address': job.address,
            'geocode_query': geocode_query,
            'display_location': display_location,
            'state': state_value,
            'state_full': state_full,
            'employment_type': job.get_employment_type_display(),
            'url': reverse('jobpostings:detail', args=[job.id]),
            'description': job.description[:100] + '...' if len(job.description) > 100 else job.description,
            'is_highlighted': is_highlighted,
        })
    
    context = {
        'jobs': jobs,
        'job_markers': job_markers,
        'search_query': search_query,
        'location_filter': location_filter,
        'employment_type_filter': employment_type_filter,
        'employment_types': JobPosting.EMPLOYMENT_TYPE_CHOICES,
        'highlighted_job': highlighted_job,
        'job_id': job_id,
    }
    
    return render(request, 'jobpostings/job_map.html', context)
