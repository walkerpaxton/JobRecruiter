from django.contrib import admin
from .models import JobPosting, Application, PipelineStage


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
	list_display = ("title", "company_name", "city", "state", "address", "employment_type", "is_active", "created_at")
	list_filter = ("employment_type", "is_active", "created_at", "state")
	search_fields = ("title", "company_name", "city", "state", "description")


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
	list_display = ("name", "order", "color", "is_final_positive", "is_final_negative", "created_at")
	list_filter = ("is_final_positive", "is_final_negative", "created_at")
	search_fields = ("name", "description")
	ordering = ("order", "name")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
	list_display = ("applicant", "job_posting", "status", "pipeline_stage", "applied_at", "stage_updated_at")
	list_filter = ("status", "pipeline_stage", "applied_at", "stage_updated_at")
	search_fields = ("applicant__username", "applicant__email", "job_posting__title", "job_posting__company_name")
	readonly_fields = ("applied_at", "updated_at", "stage_updated_at")
	ordering = ("-applied_at",)