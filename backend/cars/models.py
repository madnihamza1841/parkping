import uuid
from django.db import models
from django.conf import settings


class Car(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cars')
    plate_number = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    variant = models.CharField(max_length=100, blank=True)
    colour = models.CharField(max_length=50)
    nickname = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nickname} ({self.plate_number})'

    def get_deep_link(self):
        scheme = settings.PARKPING_APP_SCHEME
        web = settings.PARKPING_WEB_BASE_URL
        return f'{scheme}://scan/{self.uuid}', f'{web}/scan/{self.uuid}'
