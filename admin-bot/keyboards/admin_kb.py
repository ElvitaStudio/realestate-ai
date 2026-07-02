from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import math


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Пользователи", callback_data="users:0"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
        ],
        [
            InlineKeyboardButton(text="📢 Рассылка", callback_data="broadcast"),
            InlineKeyboardButton(text="🎁 Выдать Premium", callback_data="grant_premium"),
        ],
    ])


def users_list_kb(page: int, total: int, per_page: int, users: list) -> InlineKeyboardMarkup:
    total_pages = max(1, math.ceil(total / per_page))
    rows = []
    for u in users:
        name = f"{u.get('first_name') or ''} {u.get('last_name') or ''}".strip() or "—"
        uname = f"@{u['username']}" if u.get("username") else ""
        label = f"{name} {uname}".strip()
        rows.append([InlineKeyboardButton(text=label, callback_data=f"user:{u['id']}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="← Назад", callback_data=f"users:{page - 1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="→ Далее", callback_data=f"users:{page + 1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def user_card_kb(db_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👑 Выдать Premium на 30 дней", callback_data=f"action:premium30:{db_id}")],
        [InlineKeyboardButton(text="🆓 Сбросить лимит (дать 5 бесплатных)", callback_data=f"action:reset:{db_id}")],
        [InlineKeyboardButton(text="🚫 Заблокировать", callback_data=f"action:block:{db_id}")],
        [InlineKeyboardButton(text="← Назад к списку", callback_data="users:0")],
    ])


def grant_days_kb(db_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👑 30 дней", callback_data=f"grant:{db_id}:30"),
            InlineKeyboardButton(text="👑 7 дней", callback_data=f"grant:{db_id}:7"),
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="main_menu")],
    ])


def broadcast_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Отправить всем", callback_data="broadcast_confirm"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="main_menu"),
        ]
    ])


def back_to_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
