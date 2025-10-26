from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Conversation(models.Model):
    """
    Represents a conversation between two users.
    """
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        participant_names = [p.username for p in self.participants.all()]
        return f"Conversation between {', '.join(participant_names)}"
    
    def get_other_participant(self, user):
        """Get the other participant in the conversation"""
        return self.participants.exclude(id=user.id).first()
    
    def get_latest_message(self):
        """Get the latest message in the conversation"""
        return self.messages.order_by('-timestamp').first()


class Message(models.Model):
    """
    Represents a message within a conversation.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"
    
    def mark_as_read(self):
        """Mark the message as read"""
        self.is_read = True
        self.save()


class MessageNotification(models.Model):
    """
    Tracks unread message notifications for users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_notifications')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='notifications')
    unread_count = models.PositiveIntegerField(default=0)
    last_checked = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'conversation']
    
    def __str__(self):
        return f"{self.user.username} - {self.unread_count} unread messages"


class EmailMessage(models.Model):
    """
    Represents an email message sent between users.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_emails')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_emails')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Email: {self.subject} from {self.sender.username} to {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark the email as read"""
        self.is_read = True
        self.save()
    
    def send_email(self):
        """Send the email and update status"""
        from django.core.mail import send_mail
        from django.conf import settings
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # Get recipient's email address
            recipient_email = self.get_recipient_email()
            if not recipient_email:
                logger.error(f"No email address found for user {self.recipient.username}")
                self.status = 'failed'
                self.save()
                return False
            
            # Create a more detailed email body with sender information
            email_body = f"""
Hello {self.recipient.username},

You have received a new email from {self.sender.username} on JobRecruiter.

From: {self.sender.username} ({self.sender.email if self.sender.email else 'No email on file'})
Subject: {self.subject}

Message:
{self.body}

---
This email was sent from JobRecruiter platform.
If you have any questions, please contact our support team.
"""
            
            # Send the email using the system's generic email address
            send_mail(
                subject=f"[JobRecruiter] {self.subject}",
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            
            logger.info(f"Email sent successfully to {recipient_email} from {self.sender.username}")
            self.status = 'sent'
            self.sent_at = timezone.now()
            self.save()
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            self.status = 'failed'
            self.save()
            return False
    
    def get_recipient_email(self):
        """Get the recipient's email address from their Django User account"""
        return self.recipient.email if self.recipient.email else None