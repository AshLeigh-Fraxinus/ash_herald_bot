import asyncio, logging
import utils.utils as utils
from .location import request_city, validate_city, get_city_from_session
from actions.weather.weather_service import get_weather_data, parse_weather_data
from .forecast import format_weather_message, create_weather_keyboard

logger = logging.getLogger('H.weather')

async def weather_today(bot, call, session):
    await handle_weather_request(bot, call, session, "today")

async def weather_tomorrow(bot, call, session):
    await handle_weather_request(bot, call, session, "tomorrow")

async def handle_weather_request(bot, call, session, period):
    chat_id = await utils.get_chat_id(call)

    if session.state == "waiting_for_city":
        session.state = "main"
    
    city = get_city_from_session(session)
    if not city:
        logger.info(f'"{session.name}" has no city set, requesting the city')
        await request_city(bot, call, session)
        return
    logger.info(f'"{session.name}" has city set: "{city}')
    
    cnt = 16 if period == "tomorrow" else 8
    data = get_weather_data(city, cnt=str(cnt))
    if not data:
        await send_weather_error(bot, chat_id, session.name)
        return

    target_day = 1 if period == "tomorrow" else 0
    weather_data = parse_weather_data(data, target_day=target_day)
    if not weather_data:
        await send_weather_error(bot, chat_id, session.name)
        return

    message_text = format_weather_message(weather_data, period=period)
    markup = create_weather_keyboard(include_change_city=True, include_tomorrow=(period == "today"))
    await bot.send_message(chat_id, message_text, parse_mode="HTML", reply_markup=markup)

    logger.info(f'"{session.name}" received "weather_{period}"')

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

async def send_weather_error(bot, chat_id, user_name):
    logger.error(f"User: {user_name}, error in weather request")
    await bot.send_message(
        chat_id, 
        "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
        "       <i>Небеса закрыли свои врата...</i>\n"
        "<i>Облака скрыли солнце. Попробуй позже.</i>",
        parse_mode="HTML"
    )