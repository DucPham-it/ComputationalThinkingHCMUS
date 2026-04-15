"""Security helpers.

Current state:
- password hashing uses `hashlib.pbkdf2_hmac`
- access tokens use an HMAC-signed compact payload
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from app.core.config import settings

PASSWORD_ITERATIONS = 390_000
ACCESS_TOKEN_TTL_SECONDS = 60 * 60 * 24 * 7


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64decode(raw: str) -> bytes:
    padding = "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(raw + padding)


def hash_password(password: str) -> str:
    """Return hashed password string ready for database storage."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${_b64encode(salt)}${_b64encode(digest)}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a raw password against a stored hash."""
    if password_hash.startswith("hashed::"):
        return hmac.compare_digest(password_hash, f"hashed::{password}")

    try:
        algorithm, iteration_text, salt_text, digest_text = password_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    derived_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        _b64decode(salt_text),
        int(iteration_text),
    )
    return hmac.compare_digest(_b64encode(derived_digest), digest_text)


def create_access_token(user_id: int, email: str) -> str:
    """Create a signed access token for API authentication."""
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": int(time.time()) + ACCESS_TOKEN_TTL_SECONDS,
    }
    encoded_payload = _b64encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signature = hmac.new(
        settings.jwt_secret.encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{encoded_payload}.{signature}"


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Validate and decode an access token."""
    try:
        encoded_payload, signature = token.split(".", 1)
    except ValueError:
        return None

    expected_signature = hmac.new(
        settings.jwt_secret.encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        payload = json.loads(_b64decode(encoded_payload).decode("utf-8"))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None

    if int(payload.get("exp", 0)) < int(time.time()):
        return None

    return payload
