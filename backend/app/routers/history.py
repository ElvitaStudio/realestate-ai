from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Any

from app.database import get_db
from app.models import User, Generation
from app.routers.auth import get_current_user

router = APIRouter(prefix="/history", tags=["history"])


@router.get("")
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    result = await db.execute(
        select(Generation)
        .where(Generation.user_id == current_user.id)
        .order_by(Generation.created_at.desc())
    )
    generations = result.scalars().all()
    return [
        {
            "id": g.id,
            "tool_type": g.tool_type,
            "language": g.language,
            "output_preview": g.output_text[:100],
            "output_text": g.output_text,
            "created_at": g.created_at.isoformat(),
        }
        for g in generations
    ]


@router.delete("/{generation_id}")
async def delete_generation(
    generation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    result = await db.execute(
        select(Generation).where(
            Generation.id == generation_id,
            Generation.user_id == current_user.id,
        )
    )
    gen = result.scalar_one_or_none()
    if not gen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation not found")

    await db.execute(
        delete(Generation).where(
            Generation.id == generation_id,
            Generation.user_id == current_user.id,
        )
    )
    await db.commit()
    return {"status": "deleted"}
