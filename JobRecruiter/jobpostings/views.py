from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from accounts.models import Profile, JobSeekerProfile, EmployerProfile
from .models import JobPosting, Application, PipelineStage
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

@login_required
def job_delete_view(request, job_id: int):
    job = get_object_or_404(JobPosting, id=job_id)
    
    # Security check: ensure the user is the one who posted the job
    if job.posted_by != request.user:
        messages.error(request, 'You are not authorized to delete this job.')
        return redirect('jobpostings:list')
    
    if request.method == 'POST':
        job_title = job.title
        job.delete()
        messages.success(request, f'Job posting "{job_title}" has been deleted successfully.')
        return redirect('jobpostings:list')
    
    # If GET request, redirect to list page (delete should be POST only)
    messages.warning(request, 'Invalid request method.')
    return redirect('jobpostings:list')


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

@login_required
def applicant_map_view(request):
    """
    Display an interactive map showing locations of applicants who applied to the employer's jobs.
    Only shows applicants who have location sharing enabled and have a location set.
    """
    # Security Check 1: Ensure the user is an employer
    if not request.user.profile or request.user.profile.account_type != 'employer':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home.index')
    
    # Get filter parameters
    job_id = request.GET.get('job_id', '')
    applicant_id = request.GET.get('applicant_id', '')
    
    # Get all jobs posted by this employer
    employer_jobs = JobPosting.objects.filter(posted_by=request.user, is_active=True)
    
    # Filter by specific job if requested
    if job_id:
        try:
            employer_jobs = employer_jobs.filter(id=int(job_id))
        except ValueError:
            pass
    
    # Get all applications for these jobs
    applications = Application.objects.filter(job_posting__in=employer_jobs).select_related(
        'applicant', 'applicant__profile', 'applicant__profile__jobseekerprofile', 'job_posting', 'pipeline_stage'
    )
    
    # Filter to only applicants with location sharing enabled and location set
    applicant_markers = []
    highlighted_applicant = None
    
    for application in applications:
        try:
            # Check if applicant has a jobseeker profile
            if not application.applicant.profile or application.applicant.profile.account_type != 'jobseeker':
                continue
            
            try:
                jobseeker_profile = application.applicant.profile.jobseekerprofile
            except JobSeekerProfile.DoesNotExist:
                continue
            
            # Check privacy setting and location availability
            if not jobseeker_profile.show_location_to_recruiters:
                continue
            
            # Check if applicant has any location information
            if not jobseeker_profile.has_location():
                continue
            
            # Get location display string
            location_display = jobseeker_profile.get_location_display()
            if not location_display:
                continue
            
            # Check if this is the highlighted applicant
            is_highlighted = applicant_id and str(application.applicant.id) == str(applicant_id)
            if is_highlighted:
                highlighted_applicant = application
            
            # Get applicant name
            applicant_name = application.get_applicant_name()
            
            # Prepare multiple geocode query candidates for better address matching
            # This handles various formats: full addresses, city/state, city only, etc.
            geocode_candidates = []
            
            # Get cleaned field values
            address = jobseeker_profile.address.strip() if jobseeker_profile.address and jobseeker_profile.address.strip() else None
            city = jobseeker_profile.city.strip() if jobseeker_profile.city and jobseeker_profile.city.strip() else None
            state = jobseeker_profile.state.strip() if jobseeker_profile.state and jobseeker_profile.state.strip() else None
            
            # Get state variations (abbreviation and full name)
            state_variations = []
            if state:
                state_variations.append(state)
                state_full = get_state_full_name(state)
                if state_full and state_full != state:
                    state_variations.append(state_full)
            # Ensure we always have at least one state variation if state exists
            if state and len(state_variations) == 0:
                state_variations.append(state)
            
            # Build candidates in order of specificity (most specific first)
            # Always include fallbacks to less specific options in case detailed addresses fail
            
            # 1. Full address with city and state (most specific)
            if address and city and state:
                # Try different address formats - Nominatim can be picky about format
                for state_var in state_variations:
                    # Format 1: Standard "address, city, state"
                    full_address = f"{address}, {city}, {state_var}"
                    geocode_candidates.append(full_address)
                    geocode_candidates.append(f"{full_address}, USA")
                    
                    # Format 2: Try reversed order "city, state, address" (sometimes works better)
                    reversed_address = f"{city}, {state_var}, {address}"
                    geocode_candidates.append(reversed_address)
                    geocode_candidates.append(f"{reversed_address}, USA")
                
                # Fallback: city and state if full address fails (try all state variations)
                for state_var in state_variations:
                    city_state = f"{city}, {state_var}"
                    geocode_candidates.append(city_state)
                    geocode_candidates.append(f"{city_state}, USA")
                    geocode_candidates.append(f"{city_state}, United States")
            
            # 2. Address with city only
            elif address and city and not state:
                geocode_candidates.append(f"{address}, {city}")
                geocode_candidates.append(f"{address}, {city}, USA")
                # Fallback: city only
                geocode_candidates.append(city)
                geocode_candidates.append(f"{city}, USA")
            
            # 3. Address with state only
            elif address and state and not city:
                for state_var in state_variations:
                    geocode_candidates.append(f"{address}, {state_var}")
                    geocode_candidates.append(f"{address}, {state_var}, USA")
                # Fallback: state only (try all variations)
                for state_var in state_variations:
                    geocode_candidates.append(state_var)
                    geocode_candidates.append(f"{state_var}, USA")
            
            # 4. Address only
            elif address and not city and not state:
                geocode_candidates.append(address)
                geocode_candidates.append(f"{address}, USA")
            
            # 5. City and state (no address)
            elif city and state and not address:
                for state_var in state_variations:
                    city_state = f"{city}, {state_var}"
                    geocode_candidates.append(city_state)
                    geocode_candidates.append(f"{city_state}, USA")
                    geocode_candidates.append(f"{city_state}, United States")
            
            # 6. City only
            elif city and not state and not address:
                geocode_candidates.append(city)
                geocode_candidates.append(f"{city}, USA")
            
            # 7. State only (least specific, but still try)
            elif state and not city and not address:
                for state_var in state_variations:
                    geocode_candidates.append(state_var)
                    geocode_candidates.append(f"{state_var}, USA")
            
            # Remove duplicates while preserving order
            seen = set()
            unique_candidates = []
            for candidate in geocode_candidates:
                if candidate and candidate.strip() and candidate not in seen:
                    seen.add(candidate)
                    unique_candidates.append(candidate.strip())
            
            # Get pipeline stage info
            pipeline_stage_name = application.pipeline_stage.name if application.pipeline_stage else 'Unassigned'
            pipeline_stage_color = application.pipeline_stage.color if application.pipeline_stage else '#6B7280'
            
            applicant_markers.append({
                'id': application.applicant.id,
                'application_id': application.id,
                'name': applicant_name,
                'email': application.get_applicant_email(),
                'location': location_display,
                'geocode_candidates': unique_candidates,
                'geocode_query': unique_candidates[0] if unique_candidates else location_display,  # Keep for backward compatibility
                'job_title': application.job_posting.title,
                'company': application.job_posting.company_name,
                'applied_at': application.applied_at.strftime('%Y-%m-%d'),
                'pipeline_stage': pipeline_stage_name,
                'pipeline_stage_color': pipeline_stage_color,
                'profile_url': reverse('accounts.public_profile', args=[application.applicant.id]),
                'application_url': reverse('jobpostings:view_applicants', args=[application.job_posting.id]),
                'is_highlighted': is_highlighted,
            })
        except (AttributeError, JobSeekerProfile.DoesNotExist):
            continue
    
    # Get all jobs for the filter dropdown
    all_employer_jobs = JobPosting.objects.filter(posted_by=request.user, is_active=True).order_by('-created_at')
    
    # Debug: Count total applications
    total_applications = Application.objects.filter(job_posting__in=employer_jobs).count()
    
    context = {
        'applicant_markers': applicant_markers,
        'employer_jobs': all_employer_jobs,
        'selected_job_id': job_id,
        'applicant_id': applicant_id,
        'highlighted_applicant': highlighted_applicant,
        'total_applications': total_applications,
        'applicants_with_locations': len(applicant_markers),
    }
    
    return render(request, 'jobpostings/applicant_map.html', context)

@login_required
def view_applicants(request, job_id):
    # 1. Get the job post, ensuring it exists
    job = get_object_or_404(JobPosting, id=job_id)

    # 2. Security Check 1: Ensure the user is an employer
    if not request.user.profile or request.user.profile.account_type != 'employer':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home.index')

    # 3. Security Check 2: Ensure the employer owns this job posting
    if job.posted_by != request.user:
        messages.error(request, 'This is not your job posting.')
        return redirect('jobpostings:my_posted_jobs') # Send them back to their list

    # 4. Get all applications for this job.
    all_applications = job.applications.all().order_by('-applied_at')
    all_stages = PipelineStage.objects.all().order_by('order')

    context = {
        'job': job,
        'applications': all_applications,
        'pipeline_stages': all_stages
    }

    # 5. Render the new template we are about to create
    return render(request, 'jobpostings/view_applicants.html', context)


@login_required
def pipeline_view(request, job_id):
    """
    Display the Kanban board pipeline for managing applicants of a specific job.
    """
    # Get the job post, ensuring it exists
    job = get_object_or_404(JobPosting, id=job_id)

    # Security Check 1: Ensure the user is an employer
    if not request.user.profile or request.user.profile.account_type != 'employer':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home.index')

    # Security Check 2: Ensure the employer owns this job posting
    if job.posted_by != request.user:
        messages.error(request, 'This is not your job posting.')
        return redirect('jobpostings:my_posted_jobs')

    # Get all pipeline stages
    pipeline_stages = PipelineStage.objects.all().order_by('order')
    
    # Get all applications for this job, organized by pipeline stage
    applications_by_stage = {}
    for stage in pipeline_stages:
        applications_by_stage[stage.id] = {
            'stage': stage,
            'applications': job.applications.filter(pipeline_stage=stage).order_by('-applied_at')
        }
    
    # Also get applications without a pipeline stage (should be assigned to first stage)
    unassigned_applications = job.applications.filter(pipeline_stage__isnull=True).order_by('-applied_at')
    if unassigned_applications.exists() and pipeline_stages.exists():
        first_stage = pipeline_stages.first()
        if first_stage.id not in applications_by_stage:
            applications_by_stage[first_stage.id] = {
                'stage': first_stage,
                'applications': unassigned_applications
            }
        else:
            applications_by_stage[first_stage.id]['applications'] = list(applications_by_stage[first_stage.id]['applications']) + list(unassigned_applications)

    # Calculate statistics
    in_progress_count = 0
    hired_count = 0
    rejected_count = 0
    
    for stage in pipeline_stages:
        stage_apps = applications_by_stage.get(stage.id, {}).get('applications', [])
        count = len(stage_apps)
        
        if stage.is_final_positive:
            hired_count += count
        elif stage.is_final_negative:
            rejected_count += count
        else:
            in_progress_count += count

    context = {
        'job': job,
        'pipeline_stages': pipeline_stages,
        'applications_by_stage': applications_by_stage,
        'in_progress_count': in_progress_count,
        'hired_count': hired_count,
        'rejected_count': rejected_count,
    }
    

    return render(request, 'jobpostings/pipeline.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def update_application_stage(request, application_id):
    """
    Update the pipeline stage of an application via AJAX.
    """
    try:
        application = get_object_or_404(Application, id=application_id)
        
        # Security check: ensure the user owns the job posting
        if application.job_posting.posted_by != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Parse the request data
        data = json.loads(request.body)
        new_stage_id = data.get('stage_id')
        
        if new_stage_id:
            new_stage = get_object_or_404(PipelineStage, id=new_stage_id)
            application.pipeline_stage = new_stage
        else:
            application.pipeline_stage = None
        
        application.stage_updated_at = timezone.now()
        application.save()
        
        return JsonResponse({
            'success': True,
            'stage_name': application.pipeline_stage.name if application.pipeline_stage else 'Unassigned',
            'stage_color': application.pipeline_stage.color if application.pipeline_stage else '#6B7280',
            'updated_at': application.stage_updated_at.strftime('%Y-%m-%d %H:%M')
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def update_application_notes(request, application_id):
    """
    Update the notes for an application via AJAX.
    """
    try:
        application = get_object_or_404(Application, id=application_id)
        
        # Security check: ensure the user owns the job posting
        if application.job_posting.posted_by != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Parse the request data
        data = json.loads(request.body)
        notes = data.get('notes', '')
        
        application.notes = notes
        application.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def application_detail_modal(request, application_id):
    """
    Return application details for modal display.
    """
    try:
        application = get_object_or_404(Application, id=application_id)
        
        # Security check: ensure the user owns the job posting
        if application.job_posting.posted_by != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Get applicant profile information
        applicant_name = application.get_applicant_name()
        applicant_email = application.get_applicant_email()
        
        # Try to get jobseeker profile for additional details
        jobseeker_profile = None
        try:
            if application.applicant.profile.account_type == 'jobseeker':
                jobseeker_profile = application.applicant.profile.jobseekerprofile
        except:
            pass
        
        return JsonResponse({
            'success': True,
            'application': {
                'id': application.id,
                'applicant_name': applicant_name,
                'applicant_email': applicant_email,
                'cover_letter': application.cover_letter,
                'notes': application.notes,
                'applied_at': application.applied_at.strftime('%Y-%m-%d %H:%M'),
                'stage_updated_at': application.stage_updated_at.strftime('%Y-%m-%d %H:%M'),
                'pipeline_stage': {
                    'id': application.pipeline_stage.id if application.pipeline_stage else None,
                    'name': application.pipeline_stage.name if application.pipeline_stage else 'Unassigned',
                    'color': application.pipeline_stage.color if application.pipeline_stage else '#6B7280',
                } if application.pipeline_stage else None,
                'jobseeker_profile': {
                    'location': jobseeker_profile.get_location_display() if jobseeker_profile else '',
                    'phone': jobseeker_profile.phone if jobseeker_profile else '',
                    'linkedin': jobseeker_profile.linkedin if jobseeker_profile else '',
                    'summary': jobseeker_profile.summary if jobseeker_profile else '',
                    'technical_skills': jobseeker_profile.technical_skills if jobseeker_profile else '',
                    'soft_skills': jobseeker_profile.soft_skills if jobseeker_profile else '',
                    'current_job': jobseeker_profile.current_job if jobseeker_profile else '',
                    'company': jobseeker_profile.company if jobseeker_profile else '',
                    'experience_years': jobseeker_profile.experience_years if jobseeker_profile else '',
                    'resume_url': jobseeker_profile.resume.url if jobseeker_profile and jobseeker_profile.resume else None,
                } if jobseeker_profile else None,
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
@require_http_methods(["POST"]) # Only allow POST requests
def move_application_stage(request, app_id):
    # 1. Get the application object
    application = get_object_or_404(Application, id=app_id)
    job = application.job_posting # Get the related job for redirects

    # 2. Security Check: Ensure the current user owns the job posting
    if job.posted_by != request.user:
        messages.error(request, 'You do not have permission to modify this application.')
        # Redirect to a safe page, like their list of jobs
        return redirect('jobpostings:my_posted_jobs')

    # 3. Get the selected stage ID from the form's <select> input
    new_stage_id = request.POST.get('new_stage_id')

    # 4. Validate and find the PipelineStage object
    if not new_stage_id:
        messages.error(request, 'No stage was selected.')
        # Redirect back to the applicant list if nothing was chosen
        return redirect('jobpostings:view_applicants', job_id=job.id)

    try:
        new_stage = PipelineStage.objects.get(id=new_stage_id)
    except PipelineStage.DoesNotExist:
        messages.error(request, 'Invalid stage selected.')
        return redirect('jobpostings:view_applicants', job_id=job.id)

    # 5. Update the application's stage and save
    application.pipeline_stage = new_stage
    application.stage_updated_at = timezone.now() # Update timestamp
    application.save()

    messages.success(request, f"Moved {application.get_applicant_name()} to '{new_stage.name}'.")


    # 6. Redirect the user back to the pipeline view to see the change
    return redirect('jobpostings:pipeline', job_id=job.id)
