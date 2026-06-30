import httpx
from app.config import settings

MONO_API_URL = "https://api.monobank.ua/api/merchant/invoice/create"


async def create_invoice(amount_uah: int, redirect_url: str, webhook_url: str) -> dict:
    """Create Monobank invoice. Amount in kopecks (UAH * 100)."""
    payload = {
        "amount": amount_uah * 100,
        "ccy": 980,  # UAH
        "merchantPaymInfo": {
            "reference": "subscription",
            "destination": "Підписка RealEstate AI Premium",
        },
        "redirectUrl": redirect_url,
        "webHookUrl": webhook_url,
        "validity": 3600,
        "paymentType": "debit",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            MONO_API_URL,
            json=payload,
            headers={"X-Token": settings.mono_token},
        )
        resp.raise_for_status()
        return resp.json()
