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
    """Add columns introduced after initial schema creation (SQLite has no IF NOT EXISTS for columns)."""
    new_columns = [
        ("daily_generations_used", "INTEGER NOT NULL DEFAULT 0"),
        ("daily_reset_date", "DATE"),
    ]
    async with engine.begin() as conn:
        existing: list[dict] = (await conn.execute(
            __import__("sqlalchemy").text("PRAGMA table_info(users)")
        )).mappings().all()
        existing_names = {row["name"] for row in existing}
        for col_name, col_def in new_columns:
            if col_name not in existing_names:
                await conn.execute(
                    __import__("sqlalchemy").text(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
                )


async def init_db() -> None:
    from app import models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _migrate_db()
