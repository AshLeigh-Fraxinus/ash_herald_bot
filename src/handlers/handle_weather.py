import  logging

from utils import texts
from utils.keyboards import weather_keyboard
from actions.settings.change_city import change_city, get_city_name
from actions.weather.weather_data import WeatherParser, get_weather_data
from actions.weather.weather_message import format_weather_message, create_weather_keyboard
from actions.weather.graph_generator import generate_weekly_graph

logger = logging.getLogger('H.weather')

WEATHER_COMMANDS = {
    'weather_today': lambda bot, session, event: handle_weather_request(bot, session, 'today'),
    'weather_tomorrow': lambda bot, session, event: handle_weather_request(bot, session, 'tomorrow'),
    'weather_week': lambda bot, session, event: handle_weather_request(bot, session, 'week'),
    'weather_city': lambda bot, session, event: request_weather_city(bot, session),
    'weather_menu': lambda bot, session, event: handle_weather_menu(bot, session)
}

WEATHER_STATES = {
    'weather_city_and_': lambda bot, session, event: handle_city_and_weather(bot, session, event)
}

async def handle_weather(bot, session, event):
    try:
        for prefix, handler in WEATHER_STATES.items():
            if session.state.startswith(prefix):
                await handler(bot, session, event)
                return

        for prefix, handler in WEATHER_COMMANDS.items():
            if event.startswith(prefix):
                await handler(bot, session, event)
                return
            
        logger.warning(f'Unknown callback data: "{event}" from "{session.username}" in "{session.state}"')
        await bot.send_message(session.chat_id, "Неизвестная команда", parse_mode="HTML", reply_markup=weather_keyboard())

    except Exception as e:
        logger.error(f'Error handling message "{event}" for "{session.username}" in "{session.state}": {e}')
        await handle_unknown_command(bot, session)

async def handle_weather_menu(bot, session):
    session.state = "weather_menu"
    city = await get_city_name(session) if session.city and session.city != "" else "не выбран"

    await bot.send_message(
        session.chat_id,
        texts.TEXTS["WEATHER_MENU"](city),
        parse_mode="HTML",
        reply_markup=weather_keyboard()
    )
    session.update_activity()

async def handle_city_and_weather(bot, session, event):
    success = await change_city(bot, session, event)
    if success:
        handler_key = session.state.replace('weather_city_and_', '')
        session.state = "weather_menu"

        if handler_key in WEATHER_COMMANDS:
            logger.debug(f'"{session.username}" is waiting for "{handler_key}"')
            await WEATHER_COMMANDS[handler_key](bot, session, handler_key)
        else:
            await handle_weather_menu(bot, session)
        return

async def request_weather_city(bot, session):
    old_state = session.state
    session.state = f"weather_city_and_{old_state}"
    await bot.send_message(
        session.chat_id, 
        text = texts.TEXTS["CHANGE_CITY"],
        parse_mode="HTML"
    )

async def handle_weather_request(bot, session, period):
    if session.city == "":
        logger.info(f'"{session.username}" has no city set, requesting the city')
        session.state = f"weather_city_and_weather_{period}"
        await request_weather_city(bot, session)
        return

    raw_data = get_weather_data(session.city)
    
    if not raw_data:
         await bot.send_message(session.chat_id, "Не удалось связаться с метеостанцией 📡", reply_markup=weather_keyboard())
         return

    parser = WeatherParser(raw_data)
    
    weather_data = None
    period_label = "" 

    if period == "today":
        weather_data = parser.get_day_report(day_offset=0)
        period_label = "сегодня"
    elif period == "tomorrow":
        weather_data = parser.get_day_report(day_offset=1)
        period_label = "завтра"
    elif period == "week":
        weather_data = parser.get_week_report()
        period_label = "неделю"

    message_text = format_weather_message(weather_data, period_label)
    markup = create_weather_keyboard(current_view=period)
    
    session.state = "weather_menu"

    if period == "week":
        try:
            photo = generate_weekly_graph(weather_data)

            await bot.send_photo(
                session.chat_id,
                photo,
                caption=message_text,
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception as e:
            logger.error(f"Graph generation failed: {e}")
            await bot.send_message(session.chat_id, message_text, parse_mode="HTML", reply_markup=markup)
            
    else:
        await bot.send_message(
            session.chat_id, 
            message_text, 
            parse_mode="HTML", 
            reply_markup=markup
        )   
    logger.info(f'"{session.username}" received "weather_{period}"')

async def handle_unknown_command(bot, session):
    await bot.send_message(
        session.chat_id,
        text=texts.TEXTS["UNKNOWN"],
        parse_mode="HTML",
        reply_markup=weather_keyboard()
    )

