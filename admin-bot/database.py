import aiosqlite
from datetime import datetime, timedelta
from typing import Any
from config import DB_PATH


async def fetch_one(query: str, params: tuple = ()) -> dict[str, Any] | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def fetch_all(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def execute(query: str, params: tuple = ()) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(query, params)
        await db.commit()


async def get_dashboard_stats() -> dict[str, Any]:
    today = datetime.utcnow().date().isoformat()
    total = await fetch_one("SELECT COUNT(*) AS n FROM users")
    premium = await fetch_one("SELECT COUNT(*) AS n FROM users WHERE is_premium = 1")
    gens_today = await fetch_one(
        "SELECT COUNT(*) AS n FROM generations WHERE DATE(created_at) = ?", (today,)
    )
    return {
        "total": total["n"] if total else 0,
        "premium": premium["n"] if premium else 0,
        "free": (total["n"] if total else 0) - (premium["n"] if premium else 0),
        "gens_today": gens_today["n"] if gens_today else 0,
    }


async def get_users_page(page: int, per_page: int) -> tuple[list[dict[str, Any]], int]:
    offset = page * per_page
    users = await fetch_all(
        "SELECT id, telegram_id, first_name, last_name, username FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (per_page, offset),
    )
    total_row = await fetch_one("SELECT COUNT(*) AS n FROM users")
    total = total_row["n"] if total_row else 0
    return users, total


async def get_user_by_id(db_id: int) -> dict[str, Any] | None:
    return await fetch_one("SELECT * FROM users WHERE id = ?", (db_id,))


async def get_user_by_telegram_id(tg_id: int) -> dict[str, Any] | None:
    return await fetch_one("SELECT * FROM users WHERE telegram_id = ?", (tg_id,))


async def get_user_by_username(username: str) -> dict[str, Any] | None:
    clean = username.lstrip("@")
    return await fetch_one("SELECT * FROM users WHERE username = ?", (clean,))


async def grant_premium(db_id: int, days: int) -> None:
    expires = datetime.utcnow() + timedelta(days=days)
    await execute(
        "UPDATE users SET is_premium=1, subscription_expires_at=?, generations_limit=999999 WHERE id=?",
        (expires.isoformat(), db_id),
    )


async def reset_limit(db_id: int) -> None:
    await execute(
        "UPDATE users SET generations_used=0, generations_limit=5 WHERE id=?",
        (db_id,),
    )


async def block_user(db_id: int) -> None:
    await execute(
        "UPDATE users SET is_premium=0, generations_limit=0 WHERE id=?",
        (db_id,),
    )


async def get_full_stats() -> dict[str, Any]:
    today = datetime.utcnow().date().isoformat()
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    month_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()

    total = await fetch_one("SELECT COUNT(*) AS n FROM users")
    premium = await fetch_one("SELECT COUNT(*) AS n FROM users WHERE is_premium = 1")

    new_today = await fetch_one(
        "SELECT COUNT(*) AS n FROM users WHERE DATE(created_at) = ?", (today,)
    )
    new_week = await fetch_one(
        "SELECT COUNT(*) AS n FROM users WHERE created_at >= ?", (week_ago,)
    )
    new_month = await fetch_one(
        "SELECT COUNT(*) AS n FROM users WHERE created_at >= ?", (month_ago,)
    )

    gens_today = await fetch_one(
        "SELECT COUNT(*) AS n FROM generations WHERE DATE(created_at) = ?", (today,)
    )
    gens_week = await fetch_one(
        "SELECT COUNT(*) AS n FROM generations WHERE created_at >= ?", (week_ago,)
    )
    gens_month = await fetch_one(
        "SELECT COUNT(*) AS n FROM generations WHERE created_at >= ?", (month_ago,)
    )

    top_tools = await fetch_all(
        "SELECT tool_type, COUNT(*) AS cnt FROM generations GROUP BY tool_type ORDER BY cnt DESC LIMIT 7"
    )

    return {
        "total": total["n"] if total else 0,
        "premium": premium["n"] if premium else 0,
        "free": (total["n"] if total else 0) - (premium["n"] if premium else 0),
        "new_today": new_today["n"] if new_today else 0,
        "new_week": new_week["n"] if new_week else 0,
        "new_month": new_month["n"] if new_month else 0,
        "gens_today": gens_today["n"] if gens_today else 0,
        "gens_week": gens_week["n"] if gens_week else 0,
        "gens_month": gens_month["n"] if gens_month else 0,
        "top_tools": top_tools,
    }


async def get_all_telegram_ids() -> list[int]:
    rows = await fetch_all("SELECT telegram_id FROM users WHERE telegram_id IS NOT NULL")
    return [r["telegram_id"] for r in rows]


async def get_users_created_after(ts: str) -> list[dict[str, Any]]:
    return await fetch_all(
        "SELECT * FROM users WHERE created_at > ? ORDER BY created_at ASC", (ts,)
    )
