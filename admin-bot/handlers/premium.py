import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS
from database import get_user_by_telegram_id, get_user_by_username, grant_premium
from keyboards.admin_kb import grant_days_kb, back_to_menu_kb

logger = logging.getLogger(__name__)
router = Router()


class GrantPremiumFSM(StatesGroup):
    waiting_id = State()


@router.callback_query(F.data == "grant_premium")
async def cb_grant_start(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён.", show_alert=True)
        return
    await state.set_state(GrantPremiumFSM.waiting_id)
    await callback.message.edit_text(
        "🎁 <b>Выдать Premium</b>\n\nВведите Telegram ID или @username пользователя:",
        parse_mode="HTML",
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()


@router.message(GrantPremiumFSM.waiting_id)
async def grant_got_id(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    query = message.text.strip()
    u = None
    if query.startswith("@"):
        u = await get_user_by_username(query)
    else:
        try:
            u = await get_user_by_telegram_id(int(query))
        except ValueError:
            u = await get_user_by_username(query)

    if not u:
        await message.answer(
            "❌ Пользователь не найден. Попробуйте снова или нажмите 'Главное меню'.",
            reply_markup=back_to_menu_kb(),
        )
        return

    name = f"{u.get('first_name') or ''} {u.get('last_name') or ''}".strip() or "—"
    username = f"@{u['username']}" if u.get("username") else "—"
    await state.update_data(db_id=u["id"])
    await message.answer(
        f"👤 <b>{name}</b> ({username})\n"
        f"🆔 Telegram ID: <code>{u['telegram_id']}</code>\n\n"
        "На сколько дней выдать Premium?",
        parse_mode="HTML",
        reply_markup=grant_days_kb(u["id"]),
    )
    await state.clear()


@router.callback_query(F.data.startswith("grant:"))
async def cb_grant_days(callback: CallbackQuery, bot: Bot) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён.", show_alert=True)
        return
    _, db_id_str, days_str = callback.data.split(":")
    db_id, days = int(db_id_str), int(days_str)

    from database import get_user_by_id
    u = await get_user_by_id(db_id)
    if not u:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return

    await grant_premium(db_id, days)
    await callback.answer(f"✅ Premium на {days} дней выдан!", show_alert=True)

    try:
        await bot.send_message(u["telegram_id"], f"🎁 Вам выдан Premium на {days} дней! Наслаждайтесь безлимитными генерациями.")
    except Exception:
        pass

    name = f"{u.get('first_name') or ''} {u.get('last_name') or ''}".strip() or "—"
    await callback.message.edit_text(
        f"✅ <b>Premium на {days} дней выдан пользователю {name}!</b>",
        parse_mode="HTML",
        reply_markup=back_to_menu_kb(),
    )
