import base64
from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Generation, User
from app.prompts import cold_call, description, followup, incoming_call, instagram, objections, photo_description, telegram_post
from app.routers.auth import get_current_user
from app.services.claude_service import generate_text, generate_with_image

router = APIRouter(prefix="/generate", tags=["generate"])

LANGUAGE_CHOICES = {"ru", "ua", "en", "bg"}
MONTHLY_FREE_LIMIT = 100


def _is_premium_active(user: User) -> bool:
    return bool(
        user.is_premium
        and user.subscription_expires_at
        and user.subscription_expires_at > datetime.utcnow()
    )


def _first_day_of_month() -> date:
    today = date.today()
    return today.replace(day=1)


async def _check_and_reset_monthly(user: User, db: AsyncSession) -> None:
    first_of_month = _first_day_of_month()
    if user.monthly_reset_date is None or user.monthly_reset_date < first_of_month:
        user.generations_used = 0
        user.generations_limit = MONTHLY_FREE_LIMIT
        user.monthly_reset_date = first_of_month
        await db.flush()


async def _check_freemium(user: User, db: AsyncSession) -> None:
    if _is_premium_active(user):
        return
    await _check_and_reset_monthly(user, db)
    if user.generations_used >= user.generations_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Месячный лимит исчерпан. Обновитесь до Premium или возвращайтесь в следующем месяце.",
        )


async def _save_generation(
    db: AsyncSession, user: User, tool_type: str, input_data: dict, output_text: str, language: str
) -> Generation:
    gen = Generation(
        user_id=user.id,
        tool_type=tool_type,
        input_data=input_data,
        output_text=output_text,
        language=language,
    )
    db.add(gen)
    user.generations_used = user.generations_used + 1
    await db.commit()
    await db.refresh(gen)
    return gen


class DescriptionRequest(BaseModel):
    property_type: str
    rooms: str = ""
    floor: str = ""
    total_floors: str = ""
    total_area: str = ""
    living_area: str = ""
    kitchen_area: str = ""
    district: str = ""
    city: str = ""
    condition: str = ""
    features: list[str] = []
    additional: str = ""
    language: str = "ru"


class InstagramRequest(BaseModel):
    property_description: str
    tone: str = "emotional"
    use_emoji: bool = True
    language: str = "ru"


class TelegramPostRequest(BaseModel):
    property_description: str
    tone: str = "selling"
    language: str = "ru"


class ColdCallRequest(BaseModel):
    goal: str = "sell_property"
    client_type: str = "buyer"
    language: str = "ru"


class IncomingCallRequest(BaseModel):
    property_type: str
    language: str = "ru"


class ObjectionRequest(BaseModel):
    objection: str = "expensive"
    custom_objection: str = ""
    language: str = "ru"


class FollowupRequest(BaseModel):
    viewing_result: str = "thinking"
    client_feedback: str = ""
    language: str = "ru"


def _validate_language(lang: str) -> str:
    if lang not in LANGUAGE_CHOICES:
        return "ru"
    return lang


def _generation_response(gen: Generation, user: User) -> dict[str, Any]:
    is_premium = _is_premium_active(user)
    return {
        "id": gen.id,
        "output_text": gen.output_text,
        "generations_used": user.generations_used if not is_premium else 0,
        "generations_limit": user.generations_limit if not is_premium else 999999,
    }


@router.post("/description")
async def generate_description(
    req: DescriptionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await _check_freemium(current_user, db)
    lang = _validate_language(req.language)
    prompt = description.build_prompt(req.model_dump(exclude={"language"}), lang)
    output = await generate_text(prompt)
    gen = await _save_generation(db, current_user, "description", req.model_dump(), output, lang)
    return _generation_response(gen, current_user)


@router.post("/instagram")
async def generate_instagram(
    req: InstagramRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await _check_freemium(current_user, db)
    lang = _validate_language(req.language)
    prompt = instagram.build_prompt(req.model_dump(exclude={"language"}), lang)
    output = await generate_text(prompt)
    gen = await _save_generation(db, current_user, "instagram", req.model_dump(), output, lang)
    return _generation_response(gen, current_user)


@router.post("/telegram")
async def generate_telegram(
    req: TelegramPostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await _check_freemium(current_user, db)
    lang = _validate_language(req.language)
    prompt = telegram_post.build_prompt(req.model_dump(exclude={"language"}), lang)
    output = await generate_text(prompt)
    gen = await _save_generation(db, current_user, "telegram", req.model_dump(), output, lang)
    return _generation_response(gen, current_user)


@router.post("/cold-call")
async def generate_cold_call(
    req: ColdCallRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await _check_freemium(current_user, db)
    lang = _validate_language(req.language)
    prompt = cold_call.build_prompt(req.model_dump(exclude={"language"}), lang)
    output = await generate_text(prompt)
    gen = await _save_generation(db, current_user, "cold-call", req.model_dump(), output, lang)
    return _generation_response(gen, current_user)


@router.post("/incoming-call")
async def generate_incoming_call(
    req: IncomingCallRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await _check_freemium(current_user, db)
    lang = _validate_language(req.language)
    prompt = incoming_call.build_prompt(req.model_dump(exclude={"language"}), lang)
    output = await generate_text(prompt)
    gen = await _save_generation(db, current_user, "incoming-call", req.model_dump(), output, lang)
    return _generation_response(gen, current_user)


@router.post("/objection")
async def generate_objection(
    req: ObjectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await _check_freemium(current_user, db)
    lang = _validate_language(req.language)
    prompt = objections.build_prompt(req.model_dump(exclude={"language"}), lang)
    output = await generate_text(prompt)
    gen = await _save_generation(db, current_user, "objection", req.model_dump(), output, lang)
    return _generation_response(gen, current_user)


@router.post("/followup")
async def generate_followup(
    req: FollowupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await _check_freemium(current_user, db)
    lang = _validate_language(req.language)
    prompt = followup.build_prompt(req.model_dump(exclude={"language"}), lang)
    output = await generate_text(prompt)
    gen = await _save_generation(db, current_user, "followup", req.model_dump(), output, lang)
    return _generation_response(gen, current_user)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "image/jpeg",
    "image/jpg": "image/jpeg",
    "image/png": "image/png",
    "image/webp": "image/webp",
}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post("/photo-description")
async def generate_photo_description(
    photo: UploadFile = File(...),
    property_type: str = Form(default="apartment"),
    additional: str = Form(default=""),
    language: str = Form(default="ru"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await _check_freemium(current_user, db)

    content_type = (photo.content_type or "").lower()
    media_type = ALLOWED_IMAGE_TYPES.get(content_type)
    if not media_type:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Поддерживаются форматы: JPEG, PNG, WebP.",
        )

    image_bytes = await photo.read()
    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Размер файла не должен превышать 5 МБ.",
        )

    lang = _validate_language(language)
    image_b64 = base64.b64encode(image_bytes).decode()
    prompt = photo_description.build_prompt(property_type, lang, additional)
    output = await generate_with_image(prompt, image_b64, media_type)

    input_data = {"property_type": property_type, "additional": additional, "language": lang}
    gen = await _save_generation(db, current_user, "photo-description", input_data, output, lang)
    return _generation_response(gen, current_user)
