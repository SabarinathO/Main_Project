# tasks.py
from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@shared_task
def disband_expired_group(conversation_id):
    from .models import Conversation
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        if conversation.has_expired() and not conversation.extension_popup_shown:
            conversation.extension_pending = True
            conversation.extension_popup_shown = True  # Avoid repeated popups
            conversation.extension_asked_at = timezone.now()
            conversation.save()

            # Send popup only to the group admin (creator)
            channel_layer = get_channel_layer()
            admin_user_id = conversation.creator.id
            async_to_sync(channel_layer.group_send)(
                f"user_{admin_user_id}",  # Channel group name for admin user
                {
                    "type": "extension.popup",
                    "conversation_id": conversation.id,
                    "message": "Group has expired. Do you want to extend?",
                }
            )

            # Optional: Lock chat for all users except admin
            # You can broadcast this separately if needed

            # Schedule final deletion after 5 minutes if no action is taken
            delete_time = timezone.now() + timedelta(minutes=5)
            disband_expired_group_final.apply_async((conversation_id,), eta=delete_time)

    except Conversation.DoesNotExist:
        pass


@shared_task
def disband_expired_group_final(conversation_id):
    from .models import Conversation
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        conversation.creator=None  # Remove creator reference
        if conversation.extension_pending:  # No admin action within timeout
            conversation.delete()
    except Conversation.DoesNotExist:
        pass
