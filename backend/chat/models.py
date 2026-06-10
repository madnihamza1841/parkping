import uuid
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone

# Chats disappear 24 hours after the last message (see CHAT_EXPIRY_HOURS).
CHAT_EXPIRY = timedelta(hours=24)


class ChatThread(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scanner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='initiated_threads')
    car = models.ForeignKey('cars.Car', on_delete=models.CASCADE, related_name='chat_threads')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('scanner', 'car')

    def get_sender_label(self, user):
        if user == self.car.owner:
            return 'Car Owner'
        return 'Visitor'

    def other_participant(self, user):
        """The participant who is not `user`."""
        return self.car.owner if user == self.scanner else self.scanner

    @property
    def expires_at(self):
        last = self.messages.order_by('-timestamp').first()
        anchor = last.timestamp if last else self.created_at
        return anchor + CHAT_EXPIRY

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at


class Message(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)

    class Meta:
        ordering = ('timestamp',)


class Block(models.Model):
    """One user blocking another. Blocked users cannot message or call the blocker.

    Blocks are created via a thread so neither party ever needs to know the
    other's user id — anonymity is preserved.
    """
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocks_made')
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocks_received')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    @classmethod
    def exists_between(cls, user_a, user_b):
        """True if either user has blocked the other."""
        return cls.objects.filter(
            models.Q(blocker=user_a, blocked=user_b) | models.Q(blocker=user_b, blocked=user_a)
        ).exists()
