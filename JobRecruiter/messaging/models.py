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