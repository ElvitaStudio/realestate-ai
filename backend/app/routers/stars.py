import logging
import time
from datetime import datetime, timedelta
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Payment, User
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stars", tags=["stars"])

STARS_AMOUNT = 750
PREMIUM_DAYS = 30
TG_API = f"https://api.telegram.org/bot{settings.bot_token}"


class CreateInvoiceRequest(BaseModel):
    user_id: int


async def _send_invoice(telegram_id: int, payload: str) -> None:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{TG_API}/sendInvoice",
            json={
                "chat_id": telegram_id,
                "title": "RealEstate AI Premium",
                "description": "Безлимитные AI-инструменты для риелторов на 30 дней",
                "payload": payload,
                "currency": "XTR",
                "prices": [{"label": "Premium 30 дней", "amount": STARS_AMOUNT}],
            },
            timeout=10,
        )
        if not resp.is_success:
            logger.error("sendInvoice failed: %s", resp.text)
            raise HTTPException(status_code=502, detail="Не удалось отправить счёт в Telegram")


@router.post("/create-invoice")
async def create_invoice(
    body: CreateInvoiceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    result = await db.execute(select(User).where(User.id == body.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    payload = f"premium_{user.id}_{int(time.time())}"
    await _send_invoice(user.telegram_id, payload)
    return {"ok": True}


@router.post("/webhook")
async def stars_webhook(request: Request, db: AsyncSession = Depends(get_db)) -> dict[str, bool]:
    try:
        update: dict[str, Any] = await request.json()
    except Exception:
        return {"ok": True}

    message = update.get("message") or update.get("channel_post")
    if not message:
        return {"ok": True}

    payment = message.get("successful_payment")
    if not payment:
        # Handle pre_checkout_query (must answer within 10 seconds)
        pre = update.get("pre_checkout_query")
        if pre:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{TG_API}/answerPreCheckoutQuery",
                    json={"pre_checkout_query_id": pre["id"], "ok": True},
                    timeout=8,
                )
        return {"ok": True}

    payload: str = payment.get("invoice_payload", "")
    charge_id: str = payment.get("telegram_payment_charge_id", "")
    telegram_id: int = message.get("from", {}).get("id") or message.get("chat", {}).get("id")

    parts = payload.split("_")
    if len(parts) < 2 or parts[0] != "premium":
        logger.warning("Unknown Stars payload: %s", payload)
        return {"ok": True}

    try:
        user_db_id = int(parts[1])
    except ValueError:
        logger.warning("Bad user_id in payload: %s", payload)
        return {"ok": True}

    result = await db.execute(select(User).where(User.id == user_db_id))
    user = result.scalar_one_or_none()
    if not user:
        logger.warning("Stars webhook: user %s not found", user_db_id)
        return {"ok": True}

    expires = datetime.utcnow() + timedelta(days=PREMIUM_DAYS)
    user.is_premium = True
    user.subscription_expires_at = expires
    user.generations_limit = 999999

    payment_record = Payment(
        user_id=user.id,
        amount=STARS_AMOUNT,
        status="paid",
        monobank_invoice_id=charge_id,
        paid_at=datetime.utcnow(),
    )
    db.add(payment_record)
    await db.commit()

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{TG_API}/sendMessage",
                json={
                    "chat_id": telegram_id,
                    "text": (
                        "🎉 Оплата прошла успешно! Premium активирован на 30 дней. "
                        "Приятной работы на realestateai.online"
                    ),
                },
                timeout=10,
            )
    except Exception as e:
        logger.warning("Failed to send success message to user: %s", e)

    logger.info("Premium activated for user %s via Telegram Stars", user_db_id)
    return {"ok": True}


@router.get("/subscription-status")
async def subscription_status(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    now = datetime.utcnow()
    is_active = (
        current_user.is_premium
        and current_user.subscription_expires_at is not None
        and current_user.subscription_expires_at > now
    )
    days_left = 0
    if is_active and current_user.subscription_expires_at:
        days_left = (current_user.subscription_expires_at - now).days

    return {
        "is_premium": is_active,
        "expires_at": current_user.subscription_expires_at.isoformat() if current_user.subscription_expires_at else None,
        "days_left": days_left,
    }
