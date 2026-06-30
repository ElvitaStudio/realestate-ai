import hashlib
import hmac
import logging
import time
from datetime import datetime, timedelta
from typing import Any

from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.config import settings

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 30
TELEGRAM_AUTH_MAX_AGE_SECONDS = 86400  # Telegram widget data is valid for 1 day.

logger = logging.getLogger(__name__)


def verify_telegram_auth(data: dict[str, Any]) -> bool:
    """Verify Telegram Login Widget data using HMAC-SHA256.

    See https://core.telegram.org/widgets/login#checking-authorization
    """
    received_hash = data.pop("hash", None)
    if not received_hash:
        return False

    auth_date = data.get("auth_date")
    if auth_date is not None and time.time() - int(auth_date) > TELEGRAM_AUTH_MAX_AGE_SECONDS:
        logger.warning("Telegram auth rejected: auth_date too old (%s)", auth_date)
        return False

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(settings.bot_token.strip().encode()).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    # TODO(debug): remove once Telegram auth is confirmed working in production.
    logger.warning("Telegram auth data_check_string=%r", data_check_string)
    logger.warning(
        "Telegram auth received_hash=%s computed_hash=%s match=%s",
        received_hash,
        computed_hash,
        hmac.compare_digest(computed_hash, received_hash),
    )

    return hmac.compare_digest(computed_hash, received_hash)


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
