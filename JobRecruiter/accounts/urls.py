from django.urls import path
from . import views
urlpatterns = [
    path('signup/', views.signup_view, name='accounts.signup'),
    path('login/', views.login_view, name='accounts.login'),
    path('logout/', views.logout_view, name='accounts.logout'),
    path('profile/', views.profile_view, name='accounts.profile'),
    path('profile/edit/', views.edit_profile_view, name='accounts.edit_profile'),
    path('select/', views.select_account_view, name='accounts.account_select'),
    path('profile/create/jobseeker/', views.create_jobseeker_profile_view, name='accounts.create_jobseeker_profile'),
    path('profile/create/employer/', views.create_employer_profile_view, name='accounts.create_employer_profile'),
]