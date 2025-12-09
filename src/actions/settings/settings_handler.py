import logging
from telebot import types
from actions.weather.location import get_city_name
from service.sessions import session_manager
from actions.weather.weather_actions import (
    change_city, 
    handle_city_input
)
from actions.spreads.deck.change_deck import change_deck, def_deck 
from utils import keyboard
from utils.keyboard import (
    get_main_keyboard, 
    get_cards_keyboard,
    get_settings_keyboard, 
    get_weather_keyboard
)
from utils.texts import (
    SETTINGS_TEXT, 
    UNKNOWN_COMMAND_TEXT
)
import utils.utils as utils

logger = logging.getLogger('H.settings_handler')

async def handle_settings(bot, call, session):
    chat_id = await utils.get_chat_id(call)

    markup = get_settings_keyboard()
    session.state = "settings"
    city_name = await get_city_name(session)

    deck = session.deck
    deck_names = {
        'tarot': "Таро",
        'deviant_moon': "Безумной луны",
        'santa_muerte': "Святой смерти",
        'lenorman': "Ленорман",
        'persona3': "Персона 3"
    }
    deck_display = deck_names.get(deck, "Неизвестная колода")

    message_text = SETTINGS_TEXT + f"✧ Имя: {session.name}\n✧ Колода: {deck_display}\n✧ Город: {city_name}\n"
    await bot.send_message(
        chat_id, 
        message_text, 
        parse_mode="HTML", 
        reply_markup=markup
    )
    logger.info(f'"{session.name}" entered settings with "/settings"')

async def handle_change_name(bot, call, session):
    chat_id = await utils.get_chat_id(call)

    session.state = "choosing_name"
    await bot.send_message(
        chat_id, 
        "<i>Как мне к тебе обращаться?</i>\n", 
        parse_mode="HTML"
    )
    logger.info(f'"{session.name}" is now "{session.state}"')

async def handle_new_name(bot, message, session):
    chat_id = await utils.get_chat_id(message)
    deadname = session.name
    session.name = message.text
    session.state = "settings"

    await bot.send_message(
        chat_id, 
        f"<i>Рад познакомиться, {session.name}</i>\n", 
        parse_mode="HTML",
        reply_markup=keyboard.get_settings_keyboard()
    )
    logger.info(f'"{deadname}" is now "{session.name}"')