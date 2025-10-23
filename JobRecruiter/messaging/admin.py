from django.contrib import admin
from .models import Conversation, Message, MessageNotification


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_participants', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['participants__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_participants(self, obj):
        return ", ".join([p.username for p in obj.participants.all()])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'content_preview', 'timestamp', 'is_read']
    list_filter = ['is_read', 'timestamp', 'conversation']
    search_fields = ['content', 'sender__username']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(MessageNotification)
class MessageNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'conversation', 'unread_count', 'last_checked']
    list_filter = ['unread_count', 'last_checked']
    search_fields = ['user__username']