import os, datetime, requests, logging
from telebot import types

logger = logging.getLogger('WEATHER')

def get_weather_data(city):
    base_url = os.getenv("WEATHER_API_URL")
    key = os.getenv("WEATHER_API_KEY")
    
    url = base_url + city + "&cnt=5&appid=" + key
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API error {response.status_code} for city: {city}")
            return None
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        return None

def parse_weather_data(data):
    if not data:
        return None
        
    city_name = data['city']['name']
    sunrise = datetime.datetime.fromtimestamp(data['city']['sunrise']).strftime('%H:%M')
    sunset = datetime.datetime.fromtimestamp(data['city']['sunset']).strftime('%H:%M')

    current_forecast = data['list'][0]
    current_weather_code = current_forecast['weather'][0]['id']
    current_weather_symbol = get_weather_symbol(current_weather_code)

    forecasts_by_time = {}
    for forecast in data['list']:
        forecast_time = forecast['dt_txt'].split()[1]
        hour = int(forecast_time.split(':')[0])

        time_of_day = get_time_of_day(hour)
        forecasts_by_time[time_of_day] = forecast

    first_forecast = data['list'][0]
    pressure_mmhg = round(first_forecast['main']['pressure'] * 0.750062)
    wind_direction = get_wind_direction(first_forecast['wind']['deg'])
    wind_speed = first_forecast['wind']['speed']
    
    return {
        'city_name': city_name,
        'sunrise': sunrise,
        'sunset': sunset,
        'current_weather_symbol': current_weather_symbol,
        'forecasts_by_time': forecasts_by_time,
        'pressure_mmhg': pressure_mmhg,
        'wind_direction': wind_direction,
        'wind_speed': wind_speed
    }

def format_weather_message(weather_data):
    if not weather_data:
        return None
        
    message_text = (
        f"<b>══════✦ ⋆☽ {weather_data['current_weather_symbol']} ☾⋆ ✦══════</b>\n\n"
        f"<b>Погода в городе {weather_data['city_name']} на сегодня:</b>\n\n"
    )

    times_of_day = ['Утром', 'Днём', 'Вечером', 'Ночью']
    for time in times_of_day:
        if time in weather_data['forecasts_by_time']:
            forecast = weather_data['forecasts_by_time'][time]
            weather_code = forecast['weather'][0]['id'] 
            symbol = get_weather_symbol(weather_code)
            temp = round(forecast['main']['temp'])
            feels_like = round(forecast['main']['feels_like'])
            description = forecast['weather'][0]['description']
            
            message_text += f"✧ {time}:\n    ⋅    {symbol} {description}\n    ⋅    {temp}°C (ощущается как {feels_like}°C)\n"

    message_text += (
        f"\n"
        f"✧ Ветер: {weather_data['wind_direction']} {weather_data['wind_speed']} м/с\n"
        f"✧ Давление: {weather_data['pressure_mmhg']} мм рт.ст.\n\n"
        f"✧ Восход солнца: {weather_data['sunrise']}\n"
        f"✧ Закат солнца: {weather_data['sunset']}\n"
    )
    
    return message_text

def get_time_of_day(hour):
    if 6 <= hour < 12:
        return "Утром"
    elif 12 <= hour < 18:
        return "Днём"
    elif 18 <= hour < 21:
        return "Вечером"
    else:
        return "Ночью"

def get_wind_direction(degrees):
    directions = [
        (0, 22.5, "северный"),
        (22.5, 67.5, "северо-восточный"),
        (67.5, 112.5, "восточный"),
        (112.5, 157.5, "юго-восточный"),
        (157.5, 202.5, "южный"),
        (202.5, 247.5, "юго-западный"),
        (247.5, 292.5, "западный"),
        (292.5, 337.5, "северо-западный"),
        (337.5, 360, "северный")
    ]
    for min_deg, max_deg, direction in directions:
        if min_deg <= degrees < max_deg:
            return direction
    return "северный"

def get_weather_symbol(weather_code):
    WEATHER_SYMBOLS = {
        "⛈️": [200, 201, 202, 210, 211, 212, 221, 230, 231, 232],
        "🌧️": [500, 501, 502, 503, 504, 511, 520, 521, 522, 531],
        "🌨️": [600, 601, 602, 611, 612, 613, 615, 616, 620, 621, 622],
        "☁️": [741, 804],
        "☀️": [800],
        "⛅": [801, 802],
        "🌥️": [803, 804]
    }
    
    WEATHER_SYMBOLS_BY_CODE = {}
    for symbol, codes in WEATHER_SYMBOLS.items():
        for code in codes:
            WEATHER_SYMBOLS_BY_CODE[code] = symbol

    return WEATHER_SYMBOLS_BY_CODE.get(weather_code, "🌤")

def create_weather_keyboard(include_change_city=True):

    if include_change_city:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("🌆 Сменить город", callback_data="change_city")
        btn2 = types.InlineKeyboardButton("⛧ К истокам", callback_data="thanks")
        markup.add(btn1, btn2)
    else:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("⛧ К истокам", callback_data="thanks")
        markup.add(btn1)
        
    return markup