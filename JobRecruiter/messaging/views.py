from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Max
from django.utils import timezone
from .models import Conversation, Message, MessageNotification, EmailMessage
from .forms import EmailComposeForm, EmailDraftForm
from accounts.models import Profile


@login_required
def inbox(request):
    """
    Display the user's inbox with all conversations.
    """
    # Get search query
    search_query = request.GET.get('search', '').strip()
    
    # Get all conversations for the current user
    conversations = Conversation.objects.filter(participants=request.user).annotate(
        latest_message_time=Max('messages__timestamp')
    )
    
    # Apply search filter if query exists
    if search_query:
        conversations = conversations.filter(
            Q(participants__username__icontains=search_query) |
            Q(participants__first_name__icontains=search_query) |
            Q(participants__last_name__icontains=search_query) |
            Q(messages__content__icontains=search_query)
        ).distinct()
    
    conversations = conversations.order_by('-latest_message_time')
    
    # Get unread counts for each conversation
    for conversation in conversations:
        unread_count = Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user).count()
        conversation.unread_count = unread_count
    
    context = {
        'conversations': conversations,
        'search_query': search_query,
    }
    return render(request, 'messaging/inbox.html', context)


@login_required
def conversation_detail(request, conversation_id):
    """
    Display a specific conversation and allow sending messages.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    # Mark all messages in this conversation as read (except those sent by the current user)
    Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)
    
    # Get all messages in the conversation
    message_list = conversation.messages.all().order_by('timestamp')
    
    # Get the other participant
    other_participant = conversation.get_other_participant(request.user)
    
    context = {
        'conversation': conversation,
        'message_list': message_list,
        'other_participant': other_participant,
    }
    return render(request, 'messaging/conversation_detail.html', context)


@login_required
def start_conversation(request, user_id):
    """
    Start a new conversation with a specific user.
    """
    target_user = get_object_or_404(User, id=user_id)
    
    # Check if a conversation already exists between these users
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=target_user
    ).first()
    
    if existing_conversation:
        return redirect('messaging:conversation_detail', conversation_id=existing_conversation.id)
    
    # Create a new conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, target_user)
    
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)


@login_required
@require_POST
def send_message(request, conversation_id):
    """
    Send a message in a conversation.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    content = request.POST.get('content', '').strip()
    
    if not content:
        messages.error(request, "Message cannot be empty.")
        return redirect('messaging:conversation_detail', conversation_id=conversation_id)
    
    # Create the message
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )
    
    # Update conversation timestamp
    conversation.updated_at = timezone.now()
    conversation.save()
    
    return redirect('messaging:conversation_detail', conversation_id=conversation_id)


@login_required
def user_list(request):
    """
    Display a list of users that the current user can start conversations with.
    """
    # Get search query
    search_query = request.GET.get('search', '').strip()
    
    # Get all users except the current user
    users = User.objects.exclude(id=request.user.id)
    
    # Apply search filter if query exists
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    users = users.order_by('username')
    
    # Get user profiles for display
    user_profiles = []
    for user in users:
        try:
            profile = user.profile
            display_name = get_display_name(profile)
            
            # Additional search in profile-specific fields
            if search_query and profile:
                search_match = False
                if profile.account_type == 'jobseeker':
                    try:
                        jobseeker_profile = profile.jobseekerprofile
                        if (search_query.lower() in (jobseeker_profile.full_name or '').lower() or
                            search_query.lower() in (jobseeker_profile.current_job or '').lower() or
                            search_query.lower() in (jobseeker_profile.company or '').lower()):
                            search_match = True
                    except:
                        pass
                elif profile.account_type == 'employer':
                    try:
                        employer_profile = profile.employerprofile
                        if (search_query.lower() in (employer_profile.company_name or '').lower() or
                            search_query.lower() in (employer_profile.industry or '').lower()):
                            search_match = True
                    except:
                        pass
                
                # Only include if it matches the search query
                if not search_match and search_query:
                    continue
                    
            user_profiles.append({
                'user': user,
                'profile': profile,
                'display_name': display_name
            })
        except Profile.DoesNotExist:
            user_profiles.append({
                'user': user,
                'profile': None,
                'display_name': user.username
            })
    
    context = {
        'user_profiles': user_profiles,
        'search_query': search_query,
    }
    return render(request, 'messaging/user_list.html', context)


def get_display_name(profile):
    """
    Get the display name for a user based on their profile type.
    """
    if profile.account_type == 'jobseeker':
        try:
            jobseeker_profile = profile.jobseekerprofile
            return jobseeker_profile.full_name or profile.user.username
        except:
            return profile.user.username
    elif profile.account_type == 'employer':
        try:
            employer_profile = profile.employerprofile
            return employer_profile.company_name or profile.user.username
        except:
            return profile.user.username
    else:
        return profile.user.username


@login_required
def get_unread_count(request):
    """
    API endpoint to get unread message count for the current user.
    """
    unread_count = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    
    return JsonResponse({'unread_count': unread_count})


# Email Views
@login_required
def email_inbox(request):
    """
    Display the user's email inbox with received emails.
    """
    received_emails = EmailMessage.objects.filter(
        recipient=request.user,
        status='sent'
    ).order_by('-sent_at')
    
    context = {
        'received_emails': received_emails,
    }
    return render(request, 'messaging/email_inbox.html', context)


@login_required
def email_sent(request):
    """
    Display emails sent by the current user.
    """
    sent_emails = EmailMessage.objects.filter(
        sender=request.user,
        status='sent'
    ).order_by('-sent_at')
    
    context = {
        'sent_emails': sent_emails,
    }
    return render(request, 'messaging/email_sent.html', context)


@login_required
def email_drafts(request):
    """
    Display draft emails for the current user.
    """
    draft_emails = EmailMessage.objects.filter(
        sender=request.user,
        status='draft'
    ).order_by('-created_at')
    
    context = {
        'draft_emails': draft_emails,
    }
    return render(request, 'messaging/email_drafts.html', context)


@login_required
def compose_email(request):
    """
    Compose a new email.
    """
    # Check if user has an email address
    if not request.user.email:
        messages.warning(request, "You need to add an email address to your account before you can send emails.")
        return redirect('accounts.add_email')
    
    if request.method == 'POST':
        form = EmailComposeForm(request.POST, sender=request.user)
        if form.is_valid():
            email = form.save(commit=False)
            email.sender = request.user
            email.save()
            
            # Check if user wants to send immediately or save as draft
            if 'send' in request.POST:
                if email.send_email():
                    messages.success(request, f"Email sent successfully to {email.recipient.username}!")
                    return redirect('messaging:email_sent')
                else:
                    messages.error(request, "Failed to send email. Please check the recipient's email address.")
            else:
                messages.success(request, "Email saved as draft.")
                return redirect('messaging:email_drafts')
    else:
        form = EmailComposeForm(sender=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'messaging/compose_email.html', context)


@login_required
def edit_draft(request, draft_id):
    """
    Edit a draft email.
    """
    draft = get_object_or_404(EmailMessage, id=draft_id, sender=request.user, status='draft')
    
    if request.method == 'POST':
        form = EmailDraftForm(request.POST, instance=draft, sender=request.user)
        if form.is_valid():
            email = form.save()
            
            # Check if user wants to send immediately or save as draft
            if 'send' in request.POST:
                if email.send_email():
                    messages.success(request, f"Email sent successfully to {email.recipient.username}!")
                    return redirect('messaging:email_sent')
                else:
                    messages.error(request, "Failed to send email. Please check the recipient's email address.")
            else:
                messages.success(request, "Draft updated successfully.")
                return redirect('messaging:email_drafts')
    else:
        form = EmailDraftForm(instance=draft, sender=request.user)
    
    context = {
        'form': form,
        'draft': draft,
    }
    return render(request, 'messaging/edit_draft.html', context)


@login_required
def view_email(request, email_id):
    """
    View a specific email.
    """
    email = get_object_or_404(EmailMessage, id=email_id)
    
    # Check if user has permission to view this email
    if email.sender != request.user and email.recipient != request.user:
        messages.error(request, "You don't have permission to view this email.")
        return redirect('messaging:email_inbox')
    
    # Mark as read if it's a received email
    if email.recipient == request.user and not email.is_read:
        email.mark_as_read()
    
    context = {
        'email': email,
    }
    return render(request, 'messaging/view_email.html', context)


@login_required
@require_POST
def delete_email(request, email_id):
    """
    Delete an email (draft or sent).
    """
    email = get_object_or_404(EmailMessage, id=email_id, sender=request.user)
    email.delete()
    messages.success(request, "Email deleted successfully.")
    
    # Redirect based on email status
    if email.status == 'draft':
        return redirect('messaging:email_drafts')
    else:
        return redirect('messaging:email_sent')


@login_required
def send_draft(request, draft_id):
    """
    Send a draft email.
    """
    draft = get_object_or_404(EmailMessage, id=draft_id, sender=request.user, status='draft')
    
    if draft.send_email():
        messages.success(request, f"Email sent successfully to {draft.recipient.username}!")
    else:
        messages.error(request, "Failed to send email. Please check the recipient's email address.")
    
    return redirect('messaging:email_drafts')


@login_required
def user_search_api(request):
    """
    API endpoint for searching users by username for email composition.
    """
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    ).exclude(id=request.user.id)[:10]
    
    user_data = []
    for user in users:
        try:
            profile = user.profile
            if profile.account_type == 'jobseeker':
                jobseeker_profile = profile.jobseekerprofile
                display_name = jobseeker_profile.full_name or user.username
            elif profile.account_type == 'employer':
                employer_profile = profile.employerprofile
                display_name = employer_profile.company_name or user.username
            else:
                display_name = user.username
        except:
            display_name = user.username
        
        user_data.append({
            'id': user.id,
            'username': user.username,
            'display_name': display_name,
            'email': user.email,  # Use the Django User's email directly
            'has_email': bool(user.email)
        })
    
    return JsonResponse({'users': user_data})


@login_required
def debug_email_info(request, user_id):
    """
    Debug view to check email information for a user.
    """
    user = get_object_or_404(User, id=user_id)
    
    debug_info = {
        'user_id': user.id,
        'username': user.username,
        'user_email': user.email,
        'has_profile': hasattr(user, 'profile'),
    }
    
    if hasattr(user, 'profile'):
        profile = user.profile
        debug_info['profile_account_type'] = profile.account_type
        
        if profile.account_type == 'jobseeker':
            try:
                jobseeker_profile = profile.jobseekerprofile
                debug_info['jobseeker_email'] = jobseeker_profile.email
                debug_info['jobseeker_profile_exists'] = True
            except:
                debug_info['jobseeker_profile_exists'] = False
        elif profile.account_type == 'employer':
            try:
                employer_profile = profile.employerprofile
                debug_info['employer_email'] = employer_profile.email
                debug_info['employer_profile_exists'] = True
            except:
                debug_info['employer_profile_exists'] = False
    
    # Test the EmailMessage email retrieval
    try:
        from .models import EmailMessage
        test_email = EmailMessage(sender=request.user, recipient=user, subject='test', body='test')
        retrieved_email = test_email.get_recipient_email()
        debug_info['retrieved_email'] = retrieved_email
    except Exception as e:
        debug_info['email_retrieval_error'] = str(e)
    
    return JsonResponse(debug_info)


@login_required
def test_email_sending(request):
    """
    Test view to send a test email to verify SMTP configuration.
    """
    if request.method == 'POST':
        from django.core.mail import send_mail
        from django.conf import settings
        
        try:
            # Send a test email to yourself
            send_mail(
                subject='[JobRecruiter] Test Email',
                message='This is a test email to verify that your SMTP configuration is working correctly.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )
            messages.success(request, f"Test email sent successfully to {request.user.email}!")
        except Exception as e:
            messages.error(request, f"Failed to send test email: {str(e)}")
        
        return redirect('messaging:email_inbox')
    
    return render(request, 'messaging/test_email.html')