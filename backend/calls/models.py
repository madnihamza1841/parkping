import uuid
from django.db import models
from django.conf import settings


class CallLog(models.Model):
    class Status(models.TextChoices):
        INITIATED = 'initiated', 'Initiated'
        ANSWERED = 'answered', 'Answered'
        DECLINED = 'declined', 'Declined'
        MISSED = 'missed', 'Missed'
        ENDED = 'ended', 'Ended'

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey('chat.ChatThread', on_delete=models.CASCADE, related_name='calls', null=True, blank=True)
    channel_id = models.CharField(max_length=100, unique=True)
    initiated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='initiated_calls')
    car = models.ForeignKey('cars.Car', on_delete=models.CASCADE, related_name='calls')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)
    duration_seconds = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Call {self.channel_id} ({self.status})'
