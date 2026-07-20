from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Any

from app.database import get_db
from app.models import User
from app.services.auth_service import verify_telegram_auth, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()


class TelegramAuthData(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = decode_access_token(credentials.credentials)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("/telegram")
async def telegram_login(data: TelegramAuthData, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    # exclude_none=True is required: Telegram omits optional fields (last_name,
    # username, photo_url) entirely when absent, rather than sending them as
    # null. Including them as "field=None" corrupts the data_check_string and
    # makes the HMAC verification fail for every user who lacks one of these
    # fields (e.g. no username set), regardless of a correct BOT_TOKEN.
    raw = data.model_dump(exclude_none=True)
    if not verify_telegram_auth(raw):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Telegram auth data")

    result = await db.execute(select(User).where(User.telegram_id == data.id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=data.id,
            username=data.username,
            first_name=data.first_name,
            last_name=data.last_name,
            photo_url=data.photo_url,
        )
        db.add(user)
    else:
        user.username = data.username
        user.first_name = data.first_name
        user.last_name = data.last_name
        user.photo_url = data.photo_url

    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    from datetime import date, datetime
    is_premium_active = (
        current_user.is_premium
        and current_user.subscription_expires_at
        and current_user.subscription_expires_at > datetime.utcnow()
    )
    # Show 0 used if the monthly counter hasn't been reset yet this month.
    first_of_month = date.today().replace(day=1)
    monthly_used = current_user.generations_used
    if current_user.monthly_reset_date is None or current_user.monthly_reset_date < first_of_month:
        monthly_used = 0
    return {
        "id": current_user.id,
        "telegram_id": current_user.telegram_id,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "photo_url": current_user.photo_url,
        "is_premium": is_premium_active,
        "generations_used": monthly_used if not is_premium_active else 0,
        "generations_limit": current_user.generations_limit if not is_premium_active else 999999,
        "subscription_expires_at": current_user.subscription_expires_at,
    }
