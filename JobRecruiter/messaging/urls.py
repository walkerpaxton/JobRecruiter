from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Message URLs
    path('', views.inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('send/<int:conversation_id>/', views.send_message, name='send_message'),
    path('users/', views.user_list, name='user_list'),
    path('api/unread-count/', views.get_unread_count, name='unread_count'),
    
    # Email URLs
    path('email/', views.email_inbox, name='email_inbox'),
    path('email/sent/', views.email_sent, name='email_sent'),
    path('email/drafts/', views.email_drafts, name='email_drafts'),
    path('email/compose/', views.compose_email, name='compose_email'),
    path('email/draft/<int:draft_id>/edit/', views.edit_draft, name='edit_draft'),
    path('email/<int:email_id>/', views.view_email, name='view_email'),
    path('email/<int:email_id>/delete/', views.delete_email, name='delete_email'),
    path('email/draft/<int:draft_id>/send/', views.send_draft, name='send_draft'),
    path('api/user-search/', views.user_search_api, name='user_search_api'),
    path('debug/email-info/<int:user_id>/', views.debug_email_info, name='debug_email_info'),
    path('test-email/', views.test_email_sending, name='test_email_sending'),
]
