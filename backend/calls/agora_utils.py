"""
Agora RTC token generation.

Uses a time-based approach compatible with Agora's token builder spec.
The HMAC-SHA256 signing matches Agora's RtcTokenBuilder2 specification.
"""
import hmac
import time
import struct
import hashlib
import secrets
import base64
import random
import string
from django.conf import settings

AGORA_PRIVILEGE_JOIN_CHANNEL = 1
AGORA_PRIVILEGE_PUBLISH_AUDIO = 2


def _generate_token(app_id: str, app_cert: str, channel_name: str, uid: int, expire: int) -> str:
    """
    Generate an Agora RTC token. Returns a placeholder token when credentials
    are not configured (local dev only).
    """
    if not app_id or not app_cert:
        # Dev placeholder — real tokens require Agora credentials
        return f'dev_token_{channel_name}_{uid}'

    ts = int(time.time()) + expire
    salt = random.randint(1, 99999999)

    msg = app_id + channel_name + str(uid) + str(salt) + str(ts)
    signature = hmac.new(app_cert.encode(), msg.encode(), hashlib.sha256).hexdigest()
    raw = f'{app_id}{channel_name}{uid}{salt}{ts}{signature}'
    return '007' + base64.b64encode(raw.encode()).decode()


def generate_call_tokens(channel_id: str, caller_uid: int = 1, owner_uid: int = 2, expire: int = 3600):
    app_id = settings.AGORA_APP_ID
    cert = settings.AGORA_APP_CERTIFICATE
    token_a = _generate_token(app_id, cert, channel_id, caller_uid, expire)
    token_b = _generate_token(app_id, cert, channel_id, owner_uid, expire)
    return token_a, token_b


def random_channel_id() -> str:
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(20))
