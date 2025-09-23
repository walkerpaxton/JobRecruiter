from django.urls import path
from . import views

app_name = 'jobpostings'

urlpatterns = [
	path('', views.job_list_view, name='list'),
	path('create/', views.job_create_view, name='create'),
	path('<int:job_id>/', views.job_detail_view, name='detail'),
	path('<int:job_id>/edit/', views.job_edit_view, name='edit'),
] 