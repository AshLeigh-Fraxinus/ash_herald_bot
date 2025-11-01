import logging
from telebot import types

from ash_herald.actions.moon import moon_day
from ash_herald import sessions, texts
from ash_herald.handlers.spreads_handler import handle_spread, handle_spread_callback, handle_spread_message, handle_spread_waiting_state, handle_thanks
from ash_herald.utils import keyboard, utils

logger = logging.getLogger('MAIN_HANDLER')

#-------------------
# Получение текста
#-------------------
async def handle_all_messages(bot, message): 
    chat_id = await utils.get_chat_id(message)
    name_tuple = utils.get_username_and_names(message)
    name = sessions.session_manager.get_name(chat_id, name_tuple)
    session = sessions.session_manager.get_session(chat_id, name)

    if await handle_spread_waiting_state(bot, message, session):
        return

    logger.info(f"User: {session.name}, action: new message, text: {message.text}")
    
    handled = await handle_spread_message(bot, message, session)
    if handled:
        return

    handled = await main_text_handler(bot, message, session)
    if handled:
        return

    await handle_unknown_message(bot, message, session)

#------------------
# Обработка кнопок
#------------------
async def button_callback_handler(bot, call): 
    chat_id = await utils.get_chat_id(call)
    name_tuple = utils.get_username_and_names(call)
    name = sessions.session_manager.get_name(chat_id, name_tuple)
    session = sessions.session_manager.get_session(chat_id, name)

    logger.info(f"-> MAIN_HANDLER, User: {session.name}, action: {call.data}")

    try:
        await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=None 
            )
    except Exception as e:
        logger.warning(f"Could not edit message markup: {e}")
    
    logger.info(f"User: {session.name}, session: {session.state}, callback: {call.data}")
    
    try:

        handled = await handle_spread_callback(bot, call, session)
        if handled:
            return

        await main_callback_handler(bot, call, session)

    except Exception as e:
        logger.error(f"User: {session.name}, error: {e}")
        await bot.send_message(chat_id, texts.ERROR_TEXT, parse_mode="HTML")

async def main_callback_handler(bot, call, session):
    chat_id = await utils.get_chat_id(call)

    #------------------
    # Основные команды
    #------------------
    if call.data in ("start", "/start"):
        logger.info(f"-> start, User: {session.name}")
        await handle_start(bot, call)

    elif call.data == "moon_day":
        logger.info(f"-> MOON_DAY, User: {session.name}")
        await moon_day.moon_day(bot, call, session)

    elif call.data == "cards_spread":
        logger.info(f"-> CARDS_SPREAD, User: {session.name}")
        await handle_spread(bot, call)

    else:
        logger.info(f"-> MAIN_HANDLER, User: {session.name}, action: unknown callback - {call.data}")
        await bot.send_message(chat_id, texts.UNKNOWN_COMMAND_TEXT, parse_mode="HTML")

#-------------------------------
# Обработка текстовых сообщений главного меню
#-------------------------------
async def main_text_handler(bot, message, session):
    text = message.text.strip().lower()

    if text == "start":
        await handle_start(bot, message)
        return True
    
    if text in ("⛧ к истокам ⛧", "/thanks", "thanks"):
        await handle_thanks(bot, message, session)
        return True 
    
    if text in ("/cards_spread", "cards_spread", "🂠 обратиться к картам 🂠"):
        await handle_spread(bot, message)
        return True

    if text in ("☽ обратиться к луне ☾", "/moon_day", "moon_day"):
        await moon_day(bot, message, session)
        return True

    return False

#------------------
# Обработка /start
#------------------
async def handle_start(bot, message):
    chat_id = await utils.get_chat_id(message)
    name_tuple = utils.get_username_and_names(message)
    name = sessions.session_manager.get_name(chat_id, name_tuple)
    session = sessions.session_manager.get_session(chat_id, name)
    logger.info(f"User: {session.name}, action: /start")
    sessions.session_manager.reset_session(chat_id)
    await bot.send_message(chat_id, texts.START_TEXT, parse_mode="HTML", reply_markup=keyboard.get_main_keyboard())

#-------------------
# Неизвестное сообщение
#-------------------
async def handle_unknown_message(bot, message, session):
    chat_id = await utils.get_chat_id(message)
    text = message.text
    
    if session.is_waiting_for_question:
        logger.info(f"User: {session.name}, action: new message, [text]: {text}")
        session.is_waiting_for_question = False
        session.data['user_answer'] = text
        await bot.send_message(chat_id, texts.START_TEXT, parse_mode="HTML", reply_markup=keyboard.get_main_keyboard())
    else:
        logger.info(f"User: {session.name}, action: unknown command, [text]: {text}")
        await bot.send_message(chat_id, texts.UNKNOWN_COMMAND_TEXT, parse_mode="HTML")
