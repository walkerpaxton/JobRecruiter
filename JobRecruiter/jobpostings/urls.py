from django.urls import path
from . import views

urlpatterns = [
	path('', views.job_list_view, name='jobpostings.list'),
	path('create/', views.job_create_view, name='jobpostings.create'),
	path('<int:job_id>/', views.job_detail_view, name='jobpostings.detail'),
] 