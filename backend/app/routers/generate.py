from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Any

from app.database import get_db
from app.models import User, Generation
from app.routers.auth import get_current_user
from app.services.claude_service import generate_text
from app.prompts import description, instagram, telegram_post, cold_call, incoming_call, objections, followup

router = APIRouter(prefix="/generate", tags=["generate"])

LANGUAGE_CHOICES = {"ru", "ua", "en", "bg"}


def _check_freemium(user: User) -> None:
    is_premium_active = (
        user.is_premium
        and user.subscription_expires_at
        and user.subscription_expires_at > datetime.utcnow()
    )
    if not is_premium_active and user.generations_used >= user.generations_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Generation limit reached. Please upgrade to Premium.",
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
    return {
        "id": gen.id,
        "output_text": gen.output_text,
        "generations_used": user.generations_used,
        "generations_limit": user.generations_limit,
    }


@router.post("/description")
async def generate_description(
    req: DescriptionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    _check_freemium(current_user)
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
    _check_freemium(current_user)
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
    _check_freemium(current_user)
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
    _check_freemium(current_user)
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
    _check_freemium(current_user)
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
    _check_freemium(current_user)
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
    _check_freemium(current_user)
    lang = _validate_language(req.language)
    prompt = followup.build_prompt(req.model_dump(exclude={"language"}), lang)
    output = await generate_text(prompt)
    gen = await _save_generation(db, current_user, "followup", req.model_dump(), output, lang)
    return _generation_response(gen, current_user)
