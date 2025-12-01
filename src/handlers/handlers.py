import logging
from telebot import types
from service.sessions import session_manager
from actions.weather.weather_actions import (
    weather_today, 
    weather_tomorrow, 
    change_city, 
    handle_city_input
)
from actions.spreads.three_cards import (
    three_cards, 
    handle_three_cards_question
)
from actions.spreads.daily_card import daily_card
from actions.spreads.add_card import handle_additional_question
from actions.spreads.deck.choose_deck import choose_deck, def_deck  # Импорт ваших функций
from actions.moon.moon_day import moon_day
from utils.keyboard import (
    get_main_keyboard, 
    get_cards_keyboard, 
    get_deck_keyboard,
    get_weather_keyboard
)
from utils.texts import (
    START_TEXT, 
    CARDS_TEXT, 
    THANKS_TEXT, 
    UNKNOWN_COMMAND_TEXT
)
import utils.utils as utils

logger = logging.getLogger('H.handlers')

async def handle_start(bot, message):
    """Обработка команды /start"""
    chat_id = await utils.get_chat_id(message)
    name_tuple = utils.get_username_and_names(message)
    
    session = session_manager.get_session(chat_id, name_tuple)
    session.reset()
    
    markup = get_main_keyboard()
    
    await bot.send_message(
        chat_id, 
        START_TEXT, 
        parse_mode="HTML", 
        reply_markup=markup
    )
    logger.info(f"New session started for user: {session.name}")

async def handle_weather_menu(bot, call, session):
    """Обработка входа в меню погоды"""
    chat_id = await utils.get_chat_id(call)
    
    markup = get_weather_keyboard()

    await bot.send_message(
        chat_id,
        "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
        "<i>                 Погодные знамения</i>\n\n"
        "<i>Выбери, что хочешь узнать:</i>",
        parse_mode="HTML",
        reply_markup=markup
    )
    
    logger.debug(f"User: {session.name}, entered weather menu")

async def handle_cards_menu(bot, call_or_message, session=None):
    """Обработка входа в меню карт"""
    chat_id = await utils.get_chat_id(call_or_message)
    
    if session is None:
        name_tuple = utils.get_username_and_names(call_or_message)
        session = session_manager.get_session(chat_id, name_tuple)
    
    markup = get_cards_keyboard()
    
    # Пытаемся отредактировать сообщение, если это callback
    await bot.send_message(
                chat_id,
                CARDS_TEXT,
                parse_mode="HTML",
                reply_markup=markup
            )
    logger.debug(f"User: {session.name}, entered cards menu")

async def handle_thanks(bot, call, session):
    """Обработка возврата в главное меню"""
    chat_id = await utils.get_chat_id(call)
    session.reset()
    
    markup = get_main_keyboard()
    
    await bot.send_message(
                chat_id, 
                THANKS_TEXT, 
                parse_mode="HTML", 
                reply_markup=markup
            )
    logger.debug(f"User: {session.name}, returned to main menu")

async def handle_unknown_command(bot, message):
    """Обработка неизвестных команд"""
    chat_id = await utils.get_chat_id(message)
    
    await bot.send_message(
        chat_id,
        UNKNOWN_COMMAND_TEXT,
        parse_mode="HTML"
    )
    logger.warning(f"Unknown command from chat_id: {chat_id}")

async def route_callback(bot, call):
    """Маршрутизатор callback-запросов"""
    chat_id = await utils.get_chat_id(call)
    name_tuple = utils.get_username_and_names(call)
    session = session_manager.get_session(chat_id, name_tuple)
    
    callback_data = call.data
    
    try:
        # Обработка callback-действий
        if callback_data == "weather_today":
            await weather_today(bot, call, session)
            
        elif callback_data == "weather_tomorrow":
            await weather_tomorrow(bot, call, session)
            
        elif callback_data == "change_city":
            await change_city(bot, call, session)
            
        elif callback_data == "moon_day":
            await moon_day(bot, call, session)
            
        elif callback_data == "cards_spread":
            await handle_cards_menu(bot, call, session)
            
        elif callback_data == "daily_card":
            await daily_card(bot, call, session)
            
        elif callback_data == "three_cards":
            await three_cards(bot, call, session)
            
        elif callback_data == "additional_card":
            session.state = "waiting_for_additional_question"
            await handle_additional_question(bot, call, session)
            
        elif callback_data == "choose_deck":
            # Используем вашу функцию choose_deck
            await choose_deck(bot, call, session)
            
        elif callback_data in ["tarot_deck", "deviant_moon_deck", 
                              "santa_muerte_deck", "persona3_deck", 
                              "lenorman_deck"]:
            # Используем вашу функцию def_deck
            await def_deck(bot, call, session)
            
        elif callback_data == "thanks":
            await handle_thanks(bot, call, session)
            
        else:
            logger.warning(f"Unknown callback data: {callback_data} from {session.name}")
            await bot.answer_callback_query(call.id, "Неизвестная команда")
            
    except Exception as e:
        logger.error(f"Error handling callback {callback_data} for {session.name}: {e}")
        await bot.answer_callback_query(call.id, "Произошла ошибка")

async def route_message(bot, message):
    """Маршрутизатор текстовых сообщений"""
    chat_id = await utils.get_chat_id(message)
    name_tuple = utils.get_username_and_names(message)
    session = session_manager.get_session(chat_id, name_tuple)
    
    text = utils.get_text(message)
    
    try:
        # Обработка команд
        if text.startswith('/'):
            if text == '/start':
                await handle_start(bot, message)
            else:
                await handle_unknown_command(bot, message)
            return
        
        # Обработка состояний сессии
        if session.state == "waiting_for_city":
            await handle_city_input(bot, message, session)
            
        elif session.state == "waiting_for_three_cards_question":
            await handle_three_cards_question(bot, message, session)
            
        elif session.state == "waiting_for_additional_question":
            await handle_additional_question(bot, message, session)
            
        else:
            # Если пользователь просто написал текст в основном состоянии
            markup = get_main_keyboard()
            await bot.send_message(
                chat_id,
                "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
                "<i>Я понимаю только команды из меню...</i>\n\n"
                "<i>Нажми на одну из кнопок ниже,</i>\n"
                "<i>чтобы продолжить общение.</i>",
                parse_mode="HTML",
                reply_markup=markup
            )
            logger.debug(f"User: {session.name}, sent text in main state: {text[:50]}...")
            
    except Exception as e:
        logger.error(f"Error handling message for {session.name}: {e}")
        await bot.send_message(
            chat_id,
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ 🜏 ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
            "<i>Произошла ошибка при обработке запроса...</i>\n"
            "<i>Попробуйте начать сначала с /start</i>",
            parse_mode="HTML"
        )