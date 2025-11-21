from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    """
    This model acts as a central hub for a user. It stores the account type
    and links to the specific profile details (JobSeeker or Employer).
    """
    ACCOUNT_CHOICES = (
        ('jobseeker', 'Job Seeker'),
        ('employer', 'Employer'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_account_type_display()}"


class JobSeekerProfile(models.Model):
    """
    This model contains all the fields specific to a job seeker.
    It's essentially your original Profile model, but now linked to the main Profile.
    """
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, primary_key=True)
    
    # Personal Information
    full_name = models.CharField(max_length=100)
    preferred_name = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=200, blank=True, help_text="Street address")
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin = models.URLField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/jobseekers/', blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)

    show_full_name_to_recruiters = models.BooleanField(default=True)
    show_location_to_recruiters = models.BooleanField(default=True)
    show_phone_to_recruiters = models.BooleanField(default=True) 
    show_linkedin_to_recruiters = models.BooleanField(default=True)
    show_profile_picture_to_recruiters = models.BooleanField(default=True)
    show_resume_to_recruiters = models.BooleanField(default=True)
    
    # Professional Information
    summary = models.TextField(blank=True)
    technical_skills = models.TextField(blank=True)
    soft_skills = models.TextField(blank=True)

    show_summary_to_recruiters = models.BooleanField(default=True)
    show_technical_skills_to_recruiters = models.BooleanField(default=True)
    show_soft_skills_to_recruiters = models.BooleanField(default=True)
    
    # Education
    degree = models.CharField(max_length=100, blank=True)
    institution = models.CharField(max_length=100, blank=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    
    show_education_to_recruiters = models.BooleanField(default=True) # Controls all education fields

    # Work Experience
    current_job = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    experience_years = models.CharField(max_length=20, blank=True)
    availability = models.CharField(max_length=20, blank=True)
    
    show_work_experience_to_recruiters = models.BooleanField(default=True) # Controls all work history fields
    show_availability_to_recruiters = models.BooleanField(default=True)

    # Additional Information
    portfolio = models.URLField(blank=True)
    salary_expectation = models.CharField(max_length=50, blank=True)

    show_portfolio_to_recruiters = models.BooleanField(default=True)
    show_salary_expectation_to_recruiters = models.BooleanField(default=True)
    
    def get_location_display(self):
        """Combine address, city, and state into a display string"""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        return ", ".join(parts) if parts else ""
    
    def get_location_for_geocoding(self):
        """Get location string optimized for geocoding"""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        location = ", ".join(parts)
        if location and 'USA' not in location.upper() and 'United States' not in location.upper():
            location = f"{location}, USA"
        return location
    
    def has_location(self):
        """Check if any location field is filled"""
        return bool(self.address or self.city or self.state)
    
    def __str__(self):
        return f"Job Seeker Profile for {self.profile.user.username}"
    
class EmployerProfile(models.Model):
    """
    This new model contains all the fields specific to an employer or company.
    """
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, primary_key=True)
    
    # Company Information
    company_name = models.CharField(max_length=150)
    company_website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    company_logo = models.ImageField(upload_to='profile_pics/employers/', blank=True, null=True)
    
    # Company Details
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    company_description = models.TextField(blank=True)

    def __str__(self):
        return f"Employer Profile for {self.company_name}"

    