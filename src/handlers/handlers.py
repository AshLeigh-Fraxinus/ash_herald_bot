import logging
from service.sessions import session_manager
from actions.settings.settings_handler import handle_change_name, handle_new_name, handle_settings
from actions.weather.weather_actions import (
    weather_today, 
    weather_tomorrow, 
    change_city, 
    handle_city_input
)
from actions.cards.three import (
    three_cards, 
    handle_three_cards_question
)
from actions.cards.daily import daily_card
from actions.cards.add import handle_additional_question
from actions.cards.deck.change_deck import change_deck, def_deck 
from actions.moon.day import moon_day
from utils.keyboard import (
    get_main_keyboard, 
    get_cards_keyboard, 
    get_deck_keyboard,
    get_weather_keyboard
)
from utils.texts import (
    CARDS_TEXT, 
    THANKS_TEXT, 
    UNKNOWN_COMMAND_TEXT
)
import utils.utils as utils

logger = logging.getLogger('H.handlers')

async def handle_start(bot, message):
    chat_id = await utils.get_chat_id(message)
    name_tuple = utils.get_username_and_names(message)
    session = session_manager.get_session(chat_id, name_tuple)
    session.reset_state()
    
    name = utils.get_username_and_names(message, return_type="first_name")
    markup = get_main_keyboard()
    
    start_text = (
    "<b>═✦ ⋆🕯️⋆ ✦═════════════</b>\n\n"
    "<i>«Как-то в полночь, в час угрюмый,</i>\n"
    "<i> полный тягостною думой,</i>\n"
    "<i> над старинными томами</i>\n"
    "<i> я склонялся в полусне...</i>\n\n"
    "<i> Вдруг раздался стук неясный,</i>\n"
    "<i> словно кто-то постучался -</i>\n"
    "<i> постучался в дверь ко мне»</i>\n\n"
    "<b>════════════✦ ⋆ 𓅪 ⋆ ✦═</b>\n\n"
    "<i>Какой вопрос привёл тебя</i>\n"
    f"<i>к моему порогу в этот час{', ' + name if name else ''}?</i>\n\n"
    "⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ "
    )
    await bot.send_message(
        chat_id, 
        start_text, 
        parse_mode="HTML", 
        reply_markup=markup
    )
    logger.info(f'"{session.name}" now is in main menu')

async def handle_weather_menu(bot, call, session):
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
    
    logger.debug(f'"{session.name}"" entered weather menu with "{call.data}"')
    session.update_activity()

async def handle_cards_menu(bot, call_or_message, session=None):
    chat_id = await utils.get_chat_id(call_or_message)
    
    markup = get_cards_keyboard()
    await bot.send_message(
                chat_id,
                CARDS_TEXT,
                parse_mode="HTML",
                reply_markup=markup
            )
    logger.debug(f'"{session.name}" entered cards menu with "/cards_spread"')
    session.update_activity()

async def handle_thanks(bot, call, session):
    chat_id = await utils.get_chat_id(call)
    session.reset_state()
    
    markup = get_main_keyboard()
    await bot.send_message(
                chat_id, 
                THANKS_TEXT, 
                parse_mode="HTML", 
                reply_markup=markup
            )
    logger.debug(f'"{session.name}" returned to main menu with "{call.data}"')
    session.update_activity()

async def handle_unknown_command(bot, message):
    chat_id = await utils.get_chat_id(message)
    
    await bot.send_message(
        chat_id,
        UNKNOWN_COMMAND_TEXT,
        parse_mode="HTML"
    )
    logger.warning(f'"{chat_id}" sent unknown command "{message.text}"')

async def route_callback(bot, call):
    chat_id = await utils.get_chat_id(call)
    name_tuple = utils.get_username_and_names(call)
    session = session_manager.get_session(chat_id, name_tuple)
    
    callback_data = call.data
    
    try:
        session.update_activity()
        logger.debug(f'"{session.name}" requested "{callback_data}"')

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
            
        elif callback_data == "change_deck":
            await change_deck(bot, call, session)
        
        elif callback_data == "settings":
            await handle_settings(bot, call, session)

        elif callback_data == "change_name":
            await handle_change_name(bot, call, session)
            
        elif callback_data in ["deck_tarot", "deck_deviant_moon", "deck_santa_muerte", "deck_persona3", "deck_lenorman"]:
            await def_deck(bot, call, session)
            
        elif callback_data == "thanks":
            await handle_thanks(bot, call, session)
            
        else:
            logger.warning(f"Unknown callback data: {callback_data} from {session.name}")
            await bot.answer_callback_query(call.id, "Неизвестная команда")
            
    except Exception as e:
        logger.error(f'Error handling callback "{callback_data}" for "{session.name}": {e}')
        await bot.answer_callback_query(call.id, "Произошла ошибка")
        session.reset_state()

async def route_message(bot, message):
    chat_id = await utils.get_chat_id(message)
    name_tuple = utils.get_username_and_names(message)
    session = session_manager.get_session(chat_id, name_tuple)
    
    text = utils.get_text(message)
    
    try:
        session.update_activity()

        if text.startswith('/'):
            if text == '/start':
                await handle_start(bot, message)
            else:
                await handle_unknown_command(bot, message)
            return

        if session.state == "waiting_for_city":
            await handle_city_input(bot, message, session)
            
        elif session.state == "waiting_for_three_cards_question":
            await handle_three_cards_question(bot, message, session)
            
        elif session.state == "waiting_for_additional_question":
            await handle_additional_question(bot, message, session)
        
        elif session.state == "choosing_name":
            await handle_new_name(bot, message, session)
            
        else:
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
            logger.debug(f'"{session.name}" sent text in main state: "{text[:50]}..."')
            
    except Exception as e:
        logger.error(f'Error handling message for "{session.name}": {e}')
        await bot.send_message(
            chat_id,
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ 🜏 ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
            "<i>Произошла ошибка при обработке запроса...</i>\n"
            "<i>Попробуйте начать сначала с /start</i>",
            parse_mode="HTML"
        )