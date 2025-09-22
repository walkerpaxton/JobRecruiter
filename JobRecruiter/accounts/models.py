from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Personal Information
    full_name = models.CharField(max_length=100)
    preferred_name = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    linkedin = models.URLField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Professional Information
    summary = models.TextField()
    technical_skills = models.TextField(blank=True)
    soft_skills = models.TextField(blank=True)
    
    # Education
    degree = models.CharField(max_length=100, blank=True)
    institution = models.CharField(max_length=100, blank=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    
    # Work Experience
    current_job = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    experience_years = models.CharField(max_length=20, blank=True)
    availability = models.CharField(max_length=20, blank=True)
    
    # Additional Information
    languages = models.CharField(max_length=200, blank=True)
    certifications = models.TextField(blank=True)
    portfolio = models.URLField(blank=True)
    salary_expectation = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    