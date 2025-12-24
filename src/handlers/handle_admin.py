import os, logging
from typing import Dict, Any

from service.database import db_manager
from utils.keyboards import main_keyboard

logger = logging.getLogger('H.handle_admin')

def is_admin(chat_id: str) -> bool:
    admin_chat_id = os.getenv("ADMIN")
    return str(chat_id) == str(admin_chat_id)

async def handle_admin(bot, session, event):
    admin_chat_id = os.getenv("ADMIN")
    if not is_admin(session.chat_id):
        logger.warning(f'User {session.username} (chat_id: {session.chat_id}) attempted to use admin command')
        await bot.send_message(
            session.chat_id,
            text="У вас нет прав для выполнения этой команды.",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )
        await bot.send_message(
            admin_chat_id,
            text=f'@{session.username} решил что он админ',
            parse_mode="HTML"
        )
        return
    else:
        await handle_get_users_from_database(bot, session)

async def handle_get_users_from_database(bot, session):
    try:
        users = db_manager.get_all_users()
        
        if not users:
            await bot.send_message(
                session.chat_id,
                text="База данных пользователей пуста.",
                parse_mode="HTML",
                reply_markup=main_keyboard()
            )
            return

        response = f"<b>Пользователи в базе данных:</b> ({len(users)} чел.)\n\n"
        
        for i, user in enumerate(users, 1):
            username = user.get('username', 'отсутствует')
            first_name = user.get('first_name', '')
            last_name = user.get('last_name', '')
            name = user.get('name', 'не указано')
            deck = user.get('deck', 'tarot')
            city = user.get('city', 'не указан')

            created_at = user.get('created_at', 'неизвестно')
            last_activity = user.get('last_activity', 'никогда')
            last_cards_date = user.get('last_cards_daily_date', 'никогда')

            user_info = (
                f"<b>{i}. ID:</b> {user['chat_id']}\n"
                f"   <b>Имя:</b> {name}\n"
                f"   <b>Username:</b> @{username if username else 'отсутствует'}\n"
                f"   <b>Полное имя:</b> {first_name} {last_name}\n"
                f"   <b>Колода:</b> {deck}\n"
                f"   <b>Город:</b> {city}\n"
                f"   <b>Создан:</b> {created_at[:10] if len(created_at) > 10 else created_at}\n"
                f"   <b>Последняя активность:</b> {last_activity[:10] if len(last_activity) > 10 else last_activity}\n"
                f"   <b>Последняя карта дня:</b> {last_cards_date[:10] if last_cards_date and len(last_cards_date) > 10 else last_cards_date or 'никогда'}\n"
                f"   —\n"
            )

            if len(response) + len(user_info) > 4000:
                await bot.send_message(
                    session.chat_id,
                    text=response,
                    parse_mode="HTML"
                )
                response = user_info
            else:
                response += user_info

        if response:
            await bot.send_message(
                session.chat_id,
                text=response,
                parse_mode="HTML",
                reply_markup=main_keyboard()
            )
        
    except Exception as e:
        logger.error(f'Error in get_users_from_database command: {e}')
        await bot.send_message(
            session.chat_id,
            text=f"Ошибка при получении данных из базы: {str(e)}",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )
