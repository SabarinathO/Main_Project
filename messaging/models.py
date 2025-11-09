from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from .tasks import disband_expired_group
from celery import shared_task

class Conversation(models.Model):
    TIMESLOT_CHOICES = [
        ("none", "No Expiry"),
        ("hours", "Hours"),
        ("days", "Days"),
        ("months", "Months"),
    ]

    participants = models.ManyToManyField(User, related_name="conversations")
    is_groupchat = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to="profile_pics/", null=True, blank=True)
    groupname = models.CharField(max_length=100, blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_groups")
    timespan_type = models.CharField(max_length=10, choices=TIMESLOT_CHOICES, default="none")
    timespan_value = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(default=timezone.now)
    expiry_at = models.DateTimeField(null=True, blank=True)
    extension_pending = models.BooleanField(default=False)
    extension_asked_at = models.DateTimeField(null=True, blank=True)  # When we asked the admin
    extension_popup_shown = models.BooleanField(default=False)



    def save(self, *args, **kwargs):
        """Set the expiry_at field based on timespan_type and timespan_value"""
        # Check if this is a new instance (not yet saved to the database)
        is_new = self.pk is None

        if is_new:
            now = timezone.now()
            if self.timespan_type == "hours":
                self.expiry_at = now + timedelta(hours=self.timespan_value)
            elif self.timespan_type == "days":
                self.expiry_at = now + timedelta(days=self.timespan_value)
            elif self.timespan_type == "months":
                self.expiry_at = now + timedelta(days=self.timespan_value * 30)  # Approximation
            else:
                self.expiry_at = None  # No expiry for "none"

        super().save(*args, **kwargs)  # Save after setting expiry_at

        if is_new and self.expiry_at:
            delay = (self.expiry_at - timezone.now()).total_seconds()
            disband_expired_group.apply_async((self.id,), countdown=delay)
        print(f"Group created with expiry_at: {self.expiry_at} | Now: {timezone.now()}")

    def has_expired(self):
        if self.expiry_at:
            return timezone.now() >= self.expiry_at
        return False    
    

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages", null=True, blank=True)  # Only for private chats
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)  # Single Tick
    seen = models.BooleanField(default=False) 

    class Meta:
        ordering = ["timestamp"]

    def save(self, *args, **kwargs):
        """Ensure the receiver field is only set for private chats"""
        if self.conversation.is_groupchat:
            self.receiver = None  # No single receiver for group chats
        super().save(*args, **kwargs)

    def mark_as_delivered(self):
        """Mark message as delivered when received by the WebSocket"""
        self.delivered = True
        self.save()

    def mark_as_seen(self):
        """Mark message as seen when the receiver opens the chat"""
        self.seen = True
        self.save()    

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
