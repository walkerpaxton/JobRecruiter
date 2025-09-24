from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from accounts.models import Profile, JobSeekerProfile
from .models import JobPosting, Application
from .forms import JobPostingForm, ApplicationForm


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
        jobs = jobs.filter(location__icontains=location_filter)
    
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
    except Profile.DoesNotExist:
        messages.error(request, 'You must complete your profile before posting a job.')
        return redirect('accounts.profile')

    if profile.account_type != 'employer':
        messages.error(request, 'Only employers can post jobs.')
        return redirect('jobpostings:list')

    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job: JobPosting = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect(reverse('jobpostings:detail', args=[job.id]))
    else:
        form = JobPostingForm()

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
def apply_to_job_view(request, job_id: int):
    job = get_object_or_404(JobPosting, id=job_id, is_active=True)
    
    # Check if user is a job seeker
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.account_type != 'jobseeker':
            messages.error(request, 'Only job seekers can apply to jobs.')
            return redirect('jobpostings:detail', job_id=job.id)
    except Profile.DoesNotExist:
        messages.error(request, 'You must complete your profile before applying to jobs.')
        return redirect('accounts.profile')
    
    # Check if user has already applied
    if Application.objects.filter(job_posting=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied to this job.')
        return redirect('jobpostings:detail', job_id=job.id)
    
    # Get job seeker profile for pre-filling
    try:
        jobseeker_profile = JobSeekerProfile.objects.get(profile=profile)
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, 'Please complete your job seeker profile before applying.')
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
