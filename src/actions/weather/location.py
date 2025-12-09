import os, requests, logging
import utils.utils as utils

logger = logging.getLogger('H.location')

async def request_city(bot, call, session, change_city=False):
    chat_id = await utils.get_chat_id(call)
    session.state = "waiting_for_city"
    
    message_text = (
        "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
        "<i>                 Для какого города\n"
        "            хочешь узнать погоду?</i>\n\n"
        "<b>Пожалуйста, напиши город</b>\n<b>на английском языке</b>\n\n"
        "Например: Saint Petersburg"
    )

    if change_city:
        message_text = (
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
            "<i>                 Введите новый город</i>\n\n"
            "<b>Пожалуйста, напиши город</b>\n<b>на английском языке</b>\n\n"
            "Например: Saint Petersburg"
        )
    
    await bot.send_message(chat_id, message_text, parse_mode="HTML")
    logger.debug(f'"{session.name}", session set: "{session.state}", is changing city: "{change_city}"')

async def validate_city(bot, message, session):
    chat_id = await utils.get_chat_id(message)
    base_url = os.getenv("WEATHER_API_URL")
    key = os.getenv("WEATHER_API_KEY")
    
    raw_city = message.text if hasattr(message, 'text') else message
    
    city = raw_city.replace(' ', '%20')

    url = base_url + city + "&appid=" + key
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200: 
        city_name = data['city']['name']
        session.state = "main"
        session.city = city
        logger.info(f'"{session.name}" new city: "{city}"')
        return True, city_name
    else: 
        await bot.send_message(
            chat_id, 
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
            "<i>        Не удалось найти город...</i>\n\n"
            "Проверь название города:\n"
            "    Оно должно быть на\n    английском языке\n\n"
            "<b>Например: Saint Petersburg</b>",
            parse_mode="HTML"
        )
        logger.debug(f'"{session.name}" sent invalid city: "{raw_city}"')
        return False

async def get_city_name(session):
    city = session.city
    base_url = os.getenv("WEATHER_API_URL")
    key = os.getenv("WEATHER_API_KEY")
    url = base_url + city + "&appid=" + key
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200: 
        city_name = data['city']['name']
        return city_name
    else:
        return city