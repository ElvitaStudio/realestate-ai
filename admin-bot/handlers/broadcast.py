import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS, BROADCAST_DELAY
from database import get_all_telegram_ids
from keyboards.admin_kb import broadcast_confirm_kb, back_to_menu_kb

logger = logging.getLogger(__name__)
router = Router()


class BroadcastFSM(StatesGroup):
    waiting_text = State()
    confirm = State()


@router.callback_query(F.data == "broadcast")
async def cb_broadcast_start(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён.", show_alert=True)
        return
    await state.set_state(BroadcastFSM.waiting_text)
    await callback.message.edit_text(
        "📢 <b>Рассылка</b>\n\nВведите текст рассылки (поддерживается HTML):",
        parse_mode="HTML",
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()


@router.message(BroadcastFSM.waiting_text)
async def broadcast_got_text(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    text = message.html_text
    await state.update_data(text=text)
    await state.set_state(BroadcastFSM.confirm)
    await message.answer(
        f"📢 <b>Превью рассылки:</b>\n\n{text}\n\n"
        "Отправить это сообщение всем пользователям?",
        parse_mode="HTML",
        reply_markup=broadcast_confirm_kb(),
    )


@router.callback_query(F.data == "broadcast_confirm", BroadcastFSM.confirm)
async def cb_broadcast_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён.", show_alert=True)
        return
    data = await state.get_data()
    text = data.get("text", "")
    await state.clear()

    tg_ids = await get_all_telegram_ids()
    await callback.message.edit_text(
        f"⏳ Рассылка запущена, отправляю {len(tg_ids)} пользователям...",
        reply_markup=None,
    )
    await callback.answer()

    sent, errors = 0, 0
    for tg_id in tg_ids:
        try:
            await bot.send_message(tg_id, text, parse_mode="HTML")
            sent += 1
        except Exception:
            errors += 1
        await asyncio.sleep(BROADCAST_DELAY)

    await callback.message.answer(
        f"✅ Рассылка завершена.\n\nОтправлено: <b>{sent}</b>\nОшибок: <b>{errors}</b> (заблокировали бота)",
        parse_mode="HTML",
        reply_markup=back_to_menu_kb(),
    )
