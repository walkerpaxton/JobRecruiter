from .models import Message


def unread_message_count(request):
    """
    Add unread message count to template context.
    """
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        return {'unread_message_count': unread_count}
    return {'unread_message_count': 0}
