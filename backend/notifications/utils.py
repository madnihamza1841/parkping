"""
FCM push notification utility.

Initialises firebase_admin once and sends multicast messages to all
registered device tokens for a given user.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

_firebase_initialized = False


def _init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return
    creds_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', '')
    if not creds_path:
        return
    try:
        import firebase_admin
        from firebase_admin import credentials
        if not firebase_admin._apps:
            cred = credentials.Certificate(creds_path)
            firebase_admin.initialize_app(cred)
        _firebase_initialized = True
    except Exception as exc:
        logger.warning('Firebase init failed: %s', exc)


def send_push(user, title: str, body: str, data: dict = None):
    """Send FCM notification to all of user's registered device tokens."""
    _init_firebase()
    from .models import DeviceToken
    tokens = list(DeviceToken.objects.filter(user=user).values_list('token', flat=True))
    if not tokens:
        return

    try:
        from firebase_admin import messaging
        msg = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
            tokens=tokens,
        )
        response = messaging.send_each_for_multicast(msg)
        logger.info('FCM sent: %d success, %d failure', response.success_count, response.failure_count)
    except Exception as exc:
        logger.warning('FCM send failed: %s', exc)
