import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os
from typing import Any, Dict
from fastapi import HTTPException, status
from app.config import settings


def hash_password(password: str) -> str:
    """Salted SHA-256 password hash with constant-time verification."""
    salt = os.urandom(16).hex()
    pwd_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, pwd_hash = hashed_password.split("$", 1)
        test_hash = hashlib.sha256((salt + plain_password).encode("utf-8")).hexdigest()
        return hmac.compare_digest(pwd_hash, test_hash)
    except Exception:
        return False


def create_access_token(user_id: str, email: str) -> str:
    """Create a standardized JWT token."""
    header = {"alg": settings.JWT_ALGORITHM, "typ": "JWT"}
    exp = int((datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp())
    payload = {"sub": user_id, "email": email, "exp": exp}

    def b64_url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

    h_str = b64_url(json.dumps(header).encode("utf-8"))
    p_str = b64_url(json.dumps(payload).encode("utf-8"))
    sig_raw = hmac.new(settings.JWT_SECRET.encode("utf-8"), f"{h_str}.{p_str}".encode("utf-8"), hashlib.sha256).digest()
    s_str = b64_url(sig_raw)
    return f"{h_str}.{p_str}.{s_str}"


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Malformed token")
        h_str, p_str, s_str = parts

        def b64_decode(data: str) -> bytes:
            rem = len(data) % 4
            if rem > 0:
                data += "=" * (4 - rem)
            return base64.urlsafe_b64decode(data.encode("utf-8"))

        expected_sig = hmac.new(
            settings.JWT_SECRET.encode("utf-8"), f"{h_str}.{p_str}".encode("utf-8"), hashlib.sha256
        ).digest()
        actual_sig = b64_decode(s_str)
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError("Signature mismatch")

        payload = json.loads(b64_decode(p_str).decode("utf-8"))
        if payload.get("exp") and datetime.now(timezone.utc).timestamp() > payload["exp"]:
            raise ValueError("Token expired")
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
