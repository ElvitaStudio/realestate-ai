import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Any

from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.config import settings

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 30


def verify_telegram_auth(data: dict[str, Any]) -> bool:
    """Verify Telegram Login Widget data using HMAC-SHA256."""
    check_hash = data.pop("hash", None)
    if not check_hash:
        return False

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(settings.bot_token.encode()).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed_hash, check_hash)


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
