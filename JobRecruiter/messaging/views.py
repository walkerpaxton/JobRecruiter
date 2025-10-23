from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Max
from django.utils import timezone
from .models import Conversation, Message, MessageNotification
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