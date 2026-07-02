import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_IDS, NEW_USER_POLL_INTERVAL
from database import get_users_created_after
from handlers import admin, users, stats, broadcast, premium

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def poll_new_users(bot: Bot) -> None:
    last_check = datetime.utcnow().isoformat()
    while True:
        await asyncio.sleep(NEW_USER_POLL_INTERVAL)
        try:
            new_users = await get_users_created_after(last_check)
            last_check = datetime.utcnow().isoformat()
            for u in new_users:
                name = f"{u.get('first_name') or ''} {u.get('last_name') or ''}".strip() or "—"
                username = f"@{u['username']}" if u.get("username") else "—"
                text = (
                    "🆕 <b>Новый пользователь!</b>\n\n"
                    f"👤 {name}\n"
                    f"🔗 {username}\n"
                    f"🆔 <code>{u['telegram_id']}</code>"
                )
                for admin_id in ADMIN_IDS:
                    try:
                        await bot.send_message(admin_id, text, parse_mode="HTML")
                    except Exception as e:
                        logger.warning("Failed to notify admin %s: %s", admin_id, e)
        except Exception as e:
            logger.error("Error in poll_new_users: %s", e)


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(admin.router)
    dp.include_router(users.router)
    dp.include_router(stats.router)
    dp.include_router(broadcast.router)
    dp.include_router(premium.router)

    asyncio.create_task(poll_new_users(bot))

    logger.info("Admin bot starting...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
