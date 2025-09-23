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
    location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin = models.URLField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/jobseekers/', blank=True, null=True)
    
    # Professional Information
    summary = models.TextField(blank=True)
    technical_skills = models.TextField(blank=True)
    soft_skills = models.TextField(blank=True)
    
    # Education
    degree = models.CharField(max_length=100, blank=True)
    institution = models.CharField(max_length=100, blank=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    
    # Work Experience
    current_job = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    experience_years = models.CharField(max_length=20, blank=True)
    availability = models.CharField(max_length=20, blank=True)
    
    # Additional Information
    portfolio = models.URLField(blank=True)
    salary_expectation = models.CharField(max_length=50, blank=True)
    
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

    