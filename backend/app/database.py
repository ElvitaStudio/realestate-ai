from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def _migrate_db() -> None:
    """Add columns introduced after initial schema creation (SQLite lacks IF NOT EXISTS for columns)."""
    import sqlalchemy as sa

    new_columns = [
        ("monthly_reset_date", "DATE"),
    ]
    async with engine.begin() as conn:
        existing = (await conn.execute(sa.text("PRAGMA table_info(users)"))).mappings().all()
        existing_names = {row["name"] for row in existing}

        for col_name, col_def in new_columns:
            if col_name not in existing_names:
                await conn.execute(sa.text(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}"))

        # Ensure free users have the correct monthly limit.
        await conn.execute(
            sa.text("UPDATE users SET generations_limit = 100 WHERE is_premium = 0 AND generations_limit < 100")
        )


async def init_db() -> None:
    from app import models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _migrate_db()
