from django.urls import path
from . import views

app_name = 'jobpostings'

urlpatterns = [
	path('', views.job_list_view, name='list'),
	path('create/', views.job_create_view, name='create'),
	path('<int:job_id>/', views.job_detail_view, name='detail'),
	path('<int:job_id>/edit/', views.job_edit_view, name='edit'),
	path('<int:job_id>/delete/', views.job_delete_view, name='delete'),
    path('<int:job_id>/applicants/', views.view_applicants, name='view_applicants'),
    path('<int:job_id>/pipeline/', views.pipeline_view, name='pipeline'),
	path('<int:job_id>/apply/', views.apply_to_job_view, name='apply'),
	path('map/', views.job_map_view, name='map'),
    path('applicant-map/', views.applicant_map_view, name='applicant_map'),
    path('my-applications/', views.job_seeker_applications, name='job_seeker_applications'),
    path('my-posted-jobs/', views.my_posted_jobs, name='my_posted_jobs'),
    path('application/<int:app_id>/move/', views.move_application_stage, name='move_application_stage'),
    # AJAX endpoints for pipeline management

    path('application/<int:application_id>/update-stage/', views.update_application_stage, name='update_application_stage'),
    path('application/<int:application_id>/update-notes/', views.update_application_notes, name='update_application_notes'),
    path('application/<int:application_id>/detail/', views.application_detail_modal, name='application_detail_modal'),
] 