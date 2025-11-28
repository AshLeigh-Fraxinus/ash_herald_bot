import os, datetime, requests, logging
from telebot import types

logger = logging.getLogger('H.weather_service')

def get_weather_data(city, cnt):
    base_url = os.getenv("WEATHER_API_URL")
    key = os.getenv("WEATHER_API_KEY")
    
    url = base_url + city + "&cnt=" + cnt + "&appid=" + key
    
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

def parse_weather_data(data, target_day=0):
    if not data:
        return None
        
    city_name = data['city']['name']
    sunrise = datetime.datetime.fromtimestamp(data['city']['sunrise']).strftime('%H:%M')
    sunset = datetime.datetime.fromtimestamp(data['city']['sunset']).strftime('%H:%M')

    first_forecast_date = datetime.datetime.fromtimestamp(data['list'][0]['dt']).date()
    target_date = first_forecast_date + datetime.timedelta(days=target_day)
    
    forecast_date = datetime.datetime.combine(target_date, datetime.time.min)

    current_forecast = None
    for forecast in data['list']:
        forecast_dt = datetime.datetime.fromtimestamp(forecast['dt'])
        if forecast_dt.date() == target_date:
            current_forecast = forecast
            break
    
    if not current_forecast:
        current_forecast = data['list'][0] 

    current_weather_code = current_forecast['weather'][0]['id']
    current_weather_symbol = get_weather_symbol(current_weather_code)

    forecasts_by_time = {}

    day_forecasts = []
    for forecast in data['list']:
        forecast_dt = datetime.datetime.fromtimestamp(forecast['dt'])
        if forecast_dt.date() == target_date:
            day_forecasts.append(forecast)

    for forecast in day_forecasts:
        hour = int(forecast['dt_txt'].split()[1].split(':')[0])
        time_of_day = get_time_of_day(hour)

        if time_of_day not in forecasts_by_time:
            forecasts_by_time[time_of_day] = forecast
        else:
            current_hour = hour
            existing_hour = int(forecasts_by_time[time_of_day]['dt_txt'].split()[1].split(':')[0])

            if time_of_day == "Утром" and (8 <= current_hour <= 10):
                forecasts_by_time[time_of_day] = forecast
            elif time_of_day == "Днём" and (13 <= current_hour <= 15):
                forecasts_by_time[time_of_day] = forecast
            elif time_of_day == "Вечером" and (18 <= current_hour <= 20):
                forecasts_by_time[time_of_day] = forecast
            elif time_of_day == "Ночью" and (22 <= current_hour <= 23 or 0 <= current_hour <= 2):
                forecasts_by_time[time_of_day] = forecast

    first_day_forecast = day_forecasts[0] if day_forecasts else data['list'][0]
    pressure_mmhg = round(first_day_forecast['main']['pressure'] * 0.750062)
    if pressure_mmhg <= 750:
        pressure_status = "▽"
    elif pressure_mmhg >= 765:
        pressure_status = "△"
    else:
        pressure_status = "♢"
    wind_direction = get_wind_direction(first_day_forecast['wind']['deg'])
    wind_speed = first_day_forecast['wind']['speed']
    
    return {
        'date': forecast_date,
        'city_name': city_name,
        'sunrise': sunrise,
        'sunset': sunset,
        'current_weather_symbol': current_weather_symbol,
        'forecasts_by_time': forecasts_by_time,
        'pressure_mmhg': pressure_mmhg,
        'pressure_status': pressure_status,
        'wind_direction': wind_direction,
        'wind_speed': wind_speed
    }

def get_time_of_day(hour):
    if 6 <= hour < 12:
        return "Утром"
    elif 12 <= hour < 18:
        return "Днём"
    elif 18 <= hour < 24:
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
        btn1 = types.InlineKeyboardButton("☰ Сменить город", callback_data="change_city")
        btn2 = types.InlineKeyboardButton("⛧ К истокам", callback_data="thanks")
        markup.add(btn1, btn2)
    else:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("⛧ К истокам", callback_data="thanks")
        markup.add(btn1)
        
    return markup