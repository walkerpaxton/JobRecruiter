from django.contrib import admin
from .models import JobPosting, Application


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
	list_display = ("title", "company_name", "city", "state", "employment_type", "is_active", "created_at")
	list_filter = ("employment_type", "is_active", "created_at", "state")
	search_fields = ("title", "company_name", "city", "state", "description")

admin.site.register(Application)