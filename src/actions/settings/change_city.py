import os, requests, logging

from utils import texts
logger = logging.getLogger('H.city')
from service.sessions import session_manager

async def request_city(bot, session):
    await bot.send_message(
        session.chat_id, 
        text = texts.TEXTS["CHANGE_CITY"],
        parse_mode="HTML"
    )

async def change_city(bot, session, event):
    success, city_name = await validate_city(bot, session, event)
    session.sity = event
    if success:
        await bot.send_message(
            session.chat_id,
            text=(f"☰ <i>Город успешно изменен на</i> <b>{city_name}</b>"),
            parse_mode="HTML"
        )
    return True


async def validate_city(bot, session, event):
    base_url = os.getenv("WEATHER_API_URL")
    key = os.getenv("WEATHER_API_KEY")
    
    raw_city = event.text if hasattr(event, 'text') else event
    city = event.replace(' ', '%20')

    url = base_url + city + "&appid=" + key
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200: 
        city_name = data['city']['name']
        session.city = city
        logger.info(f'"{session.username}" new city: "{city}"')
        return True, city_name
    else: 
        await bot.send_message(
            session.chat_id, 
            text=(
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
            "<i>        Не удалось найти город...</i>\n\n"
            "Проверь название города:\n"
            "    Оно должно быть на\n    английском языке\n\n"
            "<b>Например: Saint Petersburg</b>"
            ),
            parse_mode="HTML"
        )
        logger.debug(f'"{session.username}" sent invalid city: "{raw_city}"')
        return False

async def get_city_name(session):
    base_url = os.getenv("WEATHER_API_URL")
    key = os.getenv("WEATHER_API_KEY")
    url = base_url + session.city + "&appid=" + key
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200: 
        city_name = data['city']['name']
        return city_name
    else:
        return session.city

