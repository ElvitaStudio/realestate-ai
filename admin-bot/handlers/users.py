import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import ADMIN_IDS, USERS_PER_PAGE
from database import get_users_page, get_user_by_id, grant_premium, reset_limit, block_user
from keyboards.admin_kb import users_list_kb, user_card_kb

logger = logging.getLogger(__name__)
router = Router()


def _user_card_text(u: dict) -> str:
    name = f"{u.get('first_name') or ''} {u.get('last_name') or ''}".strip() or "—"
    username = f"@{u['username']}" if u.get("username") else "—"
    tariff = "⭐ Premium" if u.get("is_premium") else "🆓 Free"
    premium_until = u.get("subscription_expires_at") or "—"
    if premium_until and premium_until != "—":
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(str(premium_until))
            premium_until = dt.strftime("%d.%m.%Y")
        except Exception:
            pass
    reg = "—"
    if u.get("created_at"):
        try:
            from datetime import datetime
            reg = datetime.fromisoformat(str(u["created_at"])).strftime("%d.%m.%Y")
        except Exception:
            pass
    limit = u.get("generations_limit", 5)
    limit_str = "∞" if limit >= 999999 else str(limit)

    return (
        f"👤 <b>{name}</b>\n"
        f"🆔 Telegram ID: <code>{u['telegram_id']}</code>\n"
        f"🔗 Username: {username}\n"
        f"⭐ Тариф: {tariff}\n"
        f"👑 Premium до: {premium_until}\n"
        f"📅 Регистрация: {reg}\n"
        f"⚡ Генераций использовано: <b>{u.get('generations_used', 0)}</b>\n"
        f"🔢 Лимит генераций: <b>{limit_str}</b>"
    )


@router.callback_query(F.data.startswith("users:"))
async def cb_users_list(callback: CallbackQuery) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён.", show_alert=True)
        return
    page = int(callback.data.split(":")[1])
    users, total = await get_users_page(page, USERS_PER_PAGE)
    text = f"👥 <b>Пользователи</b> (стр. {page + 1}):\n"
    kb = users_list_kb(page, total, USERS_PER_PAGE, users)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("user:"))
async def cb_user_card(callback: CallbackQuery) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён.", show_alert=True)
        return
    db_id = int(callback.data.split(":")[1])
    u = await get_user_by_id(db_id)
    if not u:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return
    await callback.message.edit_text(_user_card_text(u), reply_markup=user_card_kb(db_id), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("action:"))
async def cb_user_action(callback: CallbackQuery) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён.", show_alert=True)
        return
    parts = callback.data.split(":")
    action, db_id = parts[1], int(parts[2])
    u = await get_user_by_id(db_id)
    if not u:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return

    bot = callback.bot
    tg_id = u["telegram_id"]

    if action == "premium30":
        await grant_premium(db_id, 30)
        await callback.answer("✅ Premium на 30 дней выдан.", show_alert=True)
        try:
            await bot.send_message(tg_id, "🎁 Вам выдан Premium на 30 дней! Наслаждайтесь безлимитными генерациями.")
        except Exception:
            pass
    elif action == "reset":
        await reset_limit(db_id)
        await callback.answer("✅ Лимит сброшен — выдано 5 генераций.", show_alert=True)
        try:
            await bot.send_message(tg_id, "🆓 Ваш лимит генераций был сброшен. Вам доступно 5 бесплатных генераций.")
        except Exception:
            pass
    elif action == "block":
        await block_user(db_id)
        await callback.answer("✅ Пользователь заблокирован.", show_alert=True)
        try:
            await bot.send_message(tg_id, "🚫 Ваш аккаунт был заблокирован. Обратитесь в поддержку.")
        except Exception:
            pass

    u = await get_user_by_id(db_id)
    await callback.message.edit_text(_user_card_text(u), reply_markup=user_card_kb(db_id), parse_mode="HTML")
