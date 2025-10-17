from django.db import models
from django.contrib.auth.models import User


class JobPosting(models.Model):
    EMPLOYMENT_TYPE_CHOICES = (
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
        ('other', 'Other'),
    )

    company_name = models.CharField(max_length=150)
    title = models.CharField(max_length=150)
    city = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=50, default='')
    address = models.CharField(max_length=50, blank=True, help_text="Address")
    pay_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pay_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='USD')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    description = models.TextField()
    benefits = models.TextField(blank=True)
    application_url = models.URLField(blank=True)
    application_email = models.EmailField(blank=True)

    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='job_postings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.title} at {self.company_name}"

    def pay_range_display(self) -> str:
        if self.pay_min is not None and self.pay_max is not None:
            return f"{self.currency} {self.pay_min:,.2f} - {self.pay_max:,.2f}"
        if self.pay_min is not None:
            return f"From {self.currency} {self.pay_min:,.2f}"
        if self.pay_max is not None:
            return f"Up to {self.currency} {self.pay_max:,.2f}"
        return "Not specified"
    
    def location_display(self) -> str:
        return f"{self.city}, {self.state}"


class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('interview', 'Interview'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(help_text="Write a tailored cover letter for this specific position")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['job_posting', 'applicant']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.username} applied to {self.job_posting.title}"
