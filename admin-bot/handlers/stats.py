import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import ADMIN_IDS
from database import get_full_stats
from keyboards.admin_kb import back_to_menu_kb

logger = logging.getLogger(__name__)
router = Router()

TOOL_LABELS: dict[str, str] = {
    "description": "Описание объекта",
    "instagram": "Пост Instagram",
    "telegram": "Пост Telegram",
    "call_script": "Скрипт звонка",
    "objection": "Работа с возражениями",
    "commercial": "Коммерческое предложение",
    "presentation": "Презентация объекта",
}


@router.callback_query(F.data == "stats")
async def cb_stats(callback: CallbackQuery) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён.", show_alert=True)
        return
    s = await get_full_stats()

    tools_text = ""
    for i, tool in enumerate(s["top_tools"], 1):
        label = TOOL_LABELS.get(tool["tool_type"], tool["tool_type"])
        tools_text += f"  {i}. {label}: {tool['cnt']} раз\n"

    text = (
        "📊 <b>Статистика RealEstate AI</b>\n\n"
        f"👥 Всего пользователей: <b>{s['total']}</b>\n"
        f"⭐ Premium пользователей: <b>{s['premium']}</b>\n"
        f"🆓 Free пользователей: <b>{s['free']}</b>\n\n"
        "📈 <b>За сегодня:</b>\n"
        f"  • Новых пользователей: {s['new_today']}\n"
        f"  • Генераций: {s['gens_today']}\n\n"
        "📈 <b>За 7 дней:</b>\n"
        f"  • Новых пользователей: {s['new_week']}\n"
        f"  • Генераций: {s['gens_week']}\n\n"
        "📈 <b>За 30 дней:</b>\n"
        f"  • Новых пользователей: {s['new_month']}\n"
        f"  • Генераций: {s['gens_month']}\n\n"
        "🔧 <b>Топ инструментов (за всё время):</b>\n"
        f"{tools_text or '  Нет данных'}"
    )
    await callback.message.edit_text(text, reply_markup=back_to_menu_kb(), parse_mode="HTML")
    await callback.answer()
