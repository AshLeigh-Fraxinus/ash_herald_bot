import asyncio, logging
from telebot import types
import utils.utils as utils
from actions.weather.location import request_city, validate_city, get_city_from_session, reset_city
from actions.weather.weather_service import get_weather_data, parse_weather_data, format_weather_message, create_weather_keyboard

logger = logging.getLogger('H.weather')

async def weather_today(bot, call, session):
    chat_id = await utils.get_chat_id(call)

    if session.state == "waiting_for_city":
        session.state = "main"
    
    city = get_city_from_session(session)
    if not city:
        await request_city(bot, call, session)
        return

    data = get_weather_data(city)
    if not data:
        await send_weather_error(bot, chat_id, session.name)
        return

    weather_data = parse_weather_data(data)
    if not weather_data:
        await send_weather_error(bot, chat_id, session.name)
        return

    message_text = format_weather_message(weather_data)
    markup = create_weather_keyboard(include_change_city=True)
    await bot.send_message(chat_id, message_text, parse_mode="HTML", reply_markup=markup)

    logger.info(f"User: {session.name}, action: weather_today sent")

async def handle_city_input(bot, message, session):
    success, city_name = await validate_city(bot, message, session)

    if session.state == "waiting_for_city":
        session.state = "main"

    if success:
        await bot.send_message(
            await utils.get_chat_id(message),
            f"☰ <i>Город успешно изменен на</i> <b>{city_name}</b>",
            parse_mode="HTML"
        )
        await asyncio.sleep(1)
    await weather_today(bot, message, session)

async def change_city(bot, call, session):
    session.state = "waiting_for_city"
    await request_city(bot, call, session, change_city=True)
    logger.info(f"User: {session.name}, initiating city change")

async def send_weather_error(bot, chat_id, user_name):
    logger.error(f"User: {user_name}, error in weather_today")
    await bot.send_message(
        chat_id, 
        "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
        "       <i>Небеса закрыли свои врата...</i>\n"
        "<i>Облака скрыли солнце. Попробуй позже.</i>",
        parse_mode="HTML"
    )