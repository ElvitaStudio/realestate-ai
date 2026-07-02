import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS
from database import get_dashboard_stats
from keyboards.admin_kb import main_menu_kb

logger = logging.getLogger(__name__)
router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def send_main_menu(target: Message | CallbackQuery) -> None:
    stats = await get_dashboard_stats()
    text = (
        "👑 <b>Панель администратора</b>\n\n"
        f"👥 Пользователей: <b>{stats['total']}</b>\n"
        f"⭐ Премиум: <b>{stats['premium']}</b>\n"
        f"🆓 Free: <b>{stats['free']}</b>\n"
        f"📊 Генераций сегодня: <b>{stats['gens_today']}</b>\n\n"
        "Выберите действие:"
    )
    kb = main_menu_kb()
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await target.answer()
    else:
        await target.answer(text, reply_markup=kb, parse_mode="HTML")


@router.message(Command("start", "admin"))
async def cmd_start(message: Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещён.")
        return
    await send_main_menu(message)


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещён.", show_alert=True)
        return
    await send_main_menu(callback)
