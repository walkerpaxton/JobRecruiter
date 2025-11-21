from django.urls import path
from . import views
urlpatterns = [
    path('signup/', views.signup_view, name='accounts.signup'),
    path('login/', views.login_view, name='accounts.login'),
    path('logout/', views.logout_view, name='accounts.logout'),
    path('add-email/', views.add_email_view, name='accounts.add_email'),
    path('profile/', views.profile_view, name='accounts.profile'),
    path('profile/edit/', views.edit_profile_view, name='accounts.edit_profile'),
    path('select/', views.select_account_view, name='accounts.account_select'),
    path('profile/create/jobseeker/', views.create_jobseeker_profile_view, name='accounts.create_jobseeker_profile'),
    path('profile/create/employer/', views.create_employer_profile_view, name='accounts.create_employer_profile'),
    path('jobseeker/<int:user_id>/', views.public_profile_view, name='accounts.public_profile'),
    path('search/', views.search_candidates_view, name='search_candidates'),
    path('search/delete/<int:pk>/', views.delete_saved_search_view, name='delete_saved_search'),
    path('search/edit/<int:pk>/', views.edit_saved_search_view, name='edit_saved_search'),
]