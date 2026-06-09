"""
Agora RTC token generation — implements the Agora AccessToken2 spec.

Reference: https://docs.agora.io/en/voice-calling/reference/access-token2
"""
import hmac
import time
import struct
import hashlib
import secrets
import string
import zlib
import base64
import random
from django.conf import settings

# Agora service identifiers
SERVICE_TYPE_RTC = 1
PRIVILEGE_JOIN_CHANNEL = 1
PRIVILEGE_PUBLISH_AUDIO_STREAM = 2
PRIVILEGE_PUBLISH_VIDEO_STREAM = 3
PRIVILEGE_PUBLISH_DATA_STREAM = 4


def _pack_uint16(v: int) -> bytes:
    return struct.pack('<H', v)


def _pack_uint32(v: int) -> bytes:
    return struct.pack('<I', v)


def _pack_string(s: str) -> bytes:
    b = s.encode('utf-8')
    return _pack_uint16(len(b)) + b


def _generate_token(app_id: str, app_cert: str, channel_name: str, uid: int, expire: int) -> str:
    """Generate an Agora AccessToken2 RTC token."""
    if not app_id or not app_cert:
        return f'dev_token_{channel_name}_{uid}'

    issue_ts = int(time.time())
    expire_ts = issue_ts + expire
    salt = random.randint(1, 0x7FFFFFFF)

    # Build privileges map: privilege_id -> expire timestamp
    privileges = {
        PRIVILEGE_JOIN_CHANNEL: expire_ts,
        PRIVILEGE_PUBLISH_AUDIO_STREAM: expire_ts,
    }

    # Encode privileges
    priv_bytes = _pack_uint16(len(privileges))
    for k, v in sorted(privileges.items()):
        priv_bytes += _pack_uint16(k) + _pack_uint32(v)

    # Build service payload
    uid_str = '' if uid == 0 else str(uid)
    service_payload = (
        _pack_uint16(SERVICE_TYPE_RTC)
        + _pack_string(channel_name)
        + _pack_string(uid_str)
        + priv_bytes
    )

    # Build signing content
    sign_content = (
        _pack_string(app_id)
        + _pack_uint32(issue_ts)
        + _pack_uint32(salt)
        + service_payload
    )

    signature = hmac.new(
        bytes.fromhex(app_cert),
        sign_content,
        hashlib.sha256,
    ).digest()

    # Final token bytes
    token_bytes = (
        _pack_string(app_id)
        + _pack_uint32(issue_ts)
        + _pack_uint32(salt)
        + _pack_string(signature.hex())
        + service_payload
    )

    compressed = zlib.compress(token_bytes)
    return '007' + base64.b64encode(compressed).decode('utf-8')


def generate_call_tokens(channel_id: str, caller_uid: int = 1, owner_uid: int = 2, expire: int = 3600):
    """Return (token_a, token_b) — token_a for caller, token_b for car owner."""
    app_id = settings.AGORA_APP_ID
    cert = settings.AGORA_APP_CERTIFICATE
    token_a = _generate_token(app_id, cert, channel_id, caller_uid, expire)
    token_b = _generate_token(app_id, cert, channel_id, owner_uid, expire)
    return token_a, token_b


def random_channel_id() -> str:
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(20))
