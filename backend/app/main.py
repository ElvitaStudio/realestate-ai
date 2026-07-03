import logging
from contextlib import asynccontextmanager

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import auth, billing, generate, history, stars
from app.services.notification_service import check_expiring_subscriptions

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _setup_telegram_webhook() -> None:
    webhook_url = "https://api.realestateai.online/stars/webhook"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{settings.bot_token}/setWebhook",
                json={"url": webhook_url},
                timeout=10,
            )
        logger.info("Telegram webhook set: %s", resp.json())
    except Exception as e:
        logger.warning("Failed to set Telegram webhook: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await _setup_telegram_webhook()
    scheduler.add_job(check_expiring_subscriptions, "interval", hours=24, id="expiry_check")
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="RealEstate AI API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(generate.router)
app.include_router(history.router)
app.include_router(billing.router)
app.include_router(stars.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
