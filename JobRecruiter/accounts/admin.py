from django.contrib import admin
from .models import Profile, JobSeekerProfile, EmployerProfile

admin.site.register(Profile)
admin.site.register(JobSeekerProfile)
admin.site.register(EmployerProfile)