import logging
import time
from datetime import datetime, timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import AsyncSessionLocal as async_session_maker
from app.models import User

logger = logging.getLogger(__name__)

TG_API = f"https://api.telegram.org/bot{settings.bot_token}"
STARS_AMOUNT = 750


async def _send_renewal_invoice(telegram_id: int, user_db_id: int) -> None:
    payload = f"premium_{user_db_id}_{int(time.time())}"
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
            logger.warning("sendInvoice to %s failed: %s", telegram_id, resp.text)


async def _notify_expiring(user: User, days: int) -> None:
    if days == 3:
        text = (
            "⚠️ Ваш Premium заканчивается через 3 дня\n\n"
            "Не теряйте доступ к AI-инструментам для риелторов. Продлите подписку сейчас "
            "и продолжайте генерировать описания объектов, посты и скрипты без ограничений.\n\n"
            "💎 Premium — 750 Stars (≈$15) / месяц"
        )
        button_text = "🔄 Продлить подписку"
    else:
        text = (
            "🚨 Ваш Premium истекает завтра!\n\n"
            "Завтра вы потеряете доступ к безлимитным генерациям. "
            "Продлите сейчас чтобы не прерываться."
        )
        button_text = "🔄 Продлить сейчас"

    reply_markup = {
        "inline_keyboard": [[{"text": button_text, "callback_data": f"renew_premium_{user.id}"}]]
    }

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{TG_API}/sendMessage",
                json={
                    "chat_id": user.telegram_id,
                    "text": text,
                    "reply_markup": reply_markup,
                },
                timeout=10,
            )
        logger.info("Expiry notification sent to user %s (days=%s)", user.id, days)
    except Exception as e:
        logger.warning("Failed to notify user %s: %s", user.id, e)


async def check_expiring_subscriptions() -> None:
    logger.info("Running subscription expiry check...")
    now = datetime.utcnow()

    window_3d_start = now + timedelta(days=3)
    window_3d_end = now + timedelta(days=4)
    window_1d_start = now + timedelta(days=1)
    window_1d_end = now + timedelta(days=2)

    async with async_session_maker() as db:
        result_3d = await db.execute(
            select(User).where(
                User.is_premium.is_(True),
                User.subscription_expires_at >= window_3d_start,
                User.subscription_expires_at < window_3d_end,
            )
        )
        users_3d = result_3d.scalars().all()

        result_1d = await db.execute(
            select(User).where(
                User.is_premium.is_(True),
                User.subscription_expires_at >= window_1d_start,
                User.subscription_expires_at < window_1d_end,
            )
        )
        users_1d = result_1d.scalars().all()

    for user in users_3d:
        await _notify_expiring(user, days=3)

    for user in users_1d:
        await _notify_expiring(user, days=1)

    logger.info(
        "Expiry check done: %d users notified (3d), %d users notified (1d)",
        len(users_3d),
        len(users_1d),
    )
