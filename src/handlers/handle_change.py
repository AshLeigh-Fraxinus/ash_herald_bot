import logging

from actions.settings.change_name import change_name, request_name
from service.sessions import session_manager
from actions.settings.change_deck import change_deck, request_deck
from actions.settings.change_city import change_city, get_city_name
from utils import texts
from utils.keyboards import settings_keyboard

logger = logging.getLogger('H.settings_handler')

DECK_DISPLAY_NAMES = {
    'tarot': "Таро",
    'deviant_moon': "Безумной луны",
    'santa_muerte': "Святой смерти",
    'lenorman': "Ленорман",
    'persona3': "Персона 3"
}

CHANGE_STATES = {
    'change_city': lambda bot, session, event: handle_new_city(bot, session, event),
    'change_name': lambda bot, session, event: handle_new_name(bot, session, event),
    'change_deck': lambda bot, session, event: handle_new_deck(bot, session, event),
    }

CHANGE_COMMANDS = {
    'change_city': lambda bot, session, event: request_city(bot, session),
    'change_name': lambda bot, session, event: request_name(bot, session),
    'change_deck': lambda bot, session, event: request_deck(bot, session),
    'change_menu': lambda bot, session, event: handle_change_menu(bot, session),
    'deck_': lambda bot, session, event: handle_new_deck(bot, session, event)
}


async def handle_settings(bot, session, event):
    try:
        for prefix, handler in CHANGE_STATES.items():
            if session.state.startswith(prefix):
                await handler(bot, session, event)
                return
        for prefix, handler in CHANGE_COMMANDS.items():
            if event.startswith(prefix):
                await handler(bot, session, event)
                return
            
        logger.warning(f'Unknown callback data: "{event}" from "{session.username}" in "{session.state}"')
        await handle_unknown_command(bot, session)
            
    except Exception as e:
        logger.error(f'Error handling message "{event}" for "{session.username}" in "{session.state}": {e}')
        await handle_unknown_command(bot, session)


async def handle_change_menu(bot, session):
    deck_display = DECK_DISPLAY_NAMES.get(session.deck, "Неизвестная колода")
    name = session.name
    session.state = "change_menu"

    if session.city and session.city != "":
        city_name = await get_city_name(session)  
    else:
        city_name = ""

    await bot.send_message(
        session.chat_id, 
        text = texts.TEXTS["CHANGE_MENU"](name, deck_display, city_name), 
        parse_mode="HTML",
        reply_markup=settings_keyboard()
    )

async def handle_new_name(bot, session, event):
    await change_name(bot, session, event)
    session_manager.save_session(session.chat_id)
    session.state = "change_menu"
    await handle_change_menu(bot, session)


async def handle_new_city(bot, session, event):
    success = await change_city(bot, session, event)
    if success:
        session_manager.save_session(session.chat_id)
        await handle_change_menu(bot, session)

async def request_city(bot, session):
    await bot.send_message(
        session.chat_id, 
        text = texts.TEXTS["CHANGE_CITY"],
        parse_mode="HTML"
    )
    session.state = "change_city"

async def handle_new_deck(bot, session, event):
    success = await change_deck(bot, session, event)
    if success:
        session_manager.save_session(session.chat_id)
        await handle_change_menu(bot, session)


async def handle_unknown_command(bot, session):
    await bot.send_message(
        session.chat_id,
        text=texts.TEXTS["UNKNOWN"],
        parse_mode="HTML",
        reply_markup=settings_keyboard()
    )