"""Password hashing and stateless signed-token helpers (stdlib only)."""
import base64
import hashlib
import hmac
import json
import os
import time

from ..config import settings

_PBKDF2_ITER = 120000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITER)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$")
        salt = bytes.fromhex(salt_hex)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITER)
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64url(data: str) -> bytes:
    data += "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data)


def create_token(user_id: int, username: str, role: str) -> str:
    header = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode("utf-8"))
    payload = _b64url(json.dumps({
        "uid": user_id,
        "username": username,
        "role": role,
        "exp": int(time.time()) + settings.TOKEN_EXPIRE_HOURS * 3600,
    }).encode("utf-8"))
    signing_input = f"{header}.{payload}".encode("ascii")
    sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header}.{payload}.{_b64url(sig)}"


def verify_token(token: str, required_role: str = None):
    """Return payload dict if valid, else raise ValueError."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("token 格式错误")
    header, payload, sig = parts
    signing_input = f"{header}.{payload}".encode("ascii")
    expected = hmac.new(
        settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    actual = _unb64url(sig)
    if not hmac.compare_digest(actual, expected):
        raise ValueError("token 校验失败")
    data = json.loads(_unb64url(payload).decode("utf-8"))
    if data.get("exp", 0) < time.time():
        raise ValueError("token 已过期")
    if required_role and data.get("role") != required_role:
        raise ValueError("权限不足")
    return data
