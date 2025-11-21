from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from django.conf import settings

# Import models
from .models import JobSeekerProfile, SavedSearch
from messaging.models import Conversation, Message, MessageNotification

@receiver(post_save, sender=JobSeekerProfile)
def notify_recruiters_on_new_candidate(sender, instance, created, **kwargs):
    """
    Triggered whenever a JobSeekerProfile is saved.
    Checks all Saved Searches to see if this specific candidate is a match.
    """
    # 1. Get the candidate (instance is the JobSeekerProfile)
    candidate = instance
    
    # OPTIONAL: Only run for 'new' profiles if you want to avoid spamming on edits.
    # For a demo, it's often better to leave 'created' check OUT so you can 
    # edit an existing test user to match the keywords and see it trigger instantly.
    
    # 2. Get or Create the Bot User (The Sender)
    bot_user, _ = User.objects.get_or_create(username='CareerifyBot')
    if bot_user.password == '':
        bot_user.set_unusable_password()
        bot_user.save()

    # 3. Loop through all Saved Searches
    saved_searches = SavedSearch.objects.all()

    for search in saved_searches:
        recruiter_user = search.recruiter.profile.user
        
        # Don't notify if the candidate IS the recruiter (unlikely but good safety)
        if candidate.profile.user == recruiter_user:
            continue

        # 4. Check Logic: Does THIS candidate match THIS search?
        match = True
        
        # Location Check
        if search.location:
            # Get candidate location using the new fields
            candidate_location = candidate.get_location_display()
            if candidate_location and search.location.lower() not in candidate_location.lower():
                match = False
            elif not candidate_location:
                # If candidate has no location but search requires one, no match
                match = False
            
        # Keyword Check
        if search.keywords and match:
            # Combine candidate text fields
            candidate_text = f"{candidate.technical_skills} {candidate.soft_skills} {candidate.summary}".lower()
            if search.keywords.lower() not in candidate_text:
                match = False
        
        # 5. If it's a match, send the message!
        if match:
            # Find or Create Conversation
            conversation = Conversation.objects.filter(participants=bot_user).filter(participants=recruiter_user).first()
            
            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(bot_user, recruiter_user)

            # Check if we just sent this message (to prevent spamming during demo edits)
            # We check if the last message in this convo mentions this candidate's name
            last_msg = conversation.messages.last()
            if last_msg and candidate.full_name in last_msg.content:
                continue # Skip if we just notified them

            profile_link = settings.BASE_URL + reverse('accounts.public_profile', args=[candidate.profile.user.id])

            candidate_location = candidate.get_location_display() or "Not specified"
            msg_content = (
                f"New Match Found! \n"
                f"Candidate: {candidate.full_name} matches your '{search.name}' search.\n"
                f"Location: {candidate_location}\n"
                f"Skills: {candidate.technical_skills}\n"
                f"View Profile: {profile_link}"
            )
            
            Message.objects.create(
                conversation=conversation,
                sender=bot_user,
                content=msg_content
            )
            
            # Update Badge
            notif, _ = MessageNotification.objects.get_or_create(user=recruiter_user, conversation=conversation)
            notif.unread_count += 1
            notif.save()
            
            print(f"--- SIGNAL SENT: Notified {recruiter_user.username} about {candidate.full_name} ---")