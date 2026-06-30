import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.config import settings
from app.database import get_db
from app.models import User, Payment
from app.routers.auth import get_current_user
from app.services.billing_service import create_invoice

router = APIRouter(prefix="/billing", tags=["billing"])

SUBSCRIPTION_PRICE_UAH = 500  # ~$12


class InvoiceRequest(BaseModel):
    redirect_url: str
    webhook_url: str


@router.post("/create-invoice")
async def create_invoice_endpoint(
    req: InvoiceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    try:
        invoice_data = await create_invoice(
            amount_uah=SUBSCRIPTION_PRICE_UAH,
            redirect_url=req.redirect_url,
            webhook_url=req.webhook_url,
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    payment = Payment(
        user_id=current_user.id,
        amount=SUBSCRIPTION_PRICE_UAH * 100,
        status="pending",
        monobank_invoice_id=invoice_data.get("invoiceId"),
    )
    db.add(payment)
    await db.commit()

    return {"invoice_url": invoice_data.get("pageUrl"), "invoice_id": invoice_data.get("invoiceId")}


@router.post("/webhook")
async def monobank_webhook(request: Request, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    body = await request.body()

    if settings.mono_webhook_secret:
        signature = request.headers.get("X-Sign", "")
        expected = hmac.new(settings.mono_webhook_secret.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    import json
    data = json.loads(body)

    invoice_id = data.get("invoiceId")
    payment_status = data.get("status")

    if payment_status != "success":
        return {"status": "ignored"}

    result = await db.execute(select(Payment).where(Payment.monobank_invoice_id == invoice_id))
    payment = result.scalar_one_or_none()
    if not payment:
        return {"status": "payment not found"}

    payment.status = "paid"
    payment.paid_at = datetime.utcnow()

    user_result = await db.execute(select(User).where(User.id == payment.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.is_premium = True
        user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)

    await db.commit()
    return {"status": "ok"}


@router.get("/status")
async def billing_status(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    is_active = (
        current_user.is_premium
        and current_user.subscription_expires_at
        and current_user.subscription_expires_at > datetime.utcnow()
    )
    return {
        "is_premium": bool(is_active),
        "subscription_expires_at": (
            current_user.subscription_expires_at.isoformat()
            if current_user.subscription_expires_at
            else None
        ),
    }
