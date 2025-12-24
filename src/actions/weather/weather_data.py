import os, datetime, requests, logging
from datetime import timezone

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
            logger.error(f'API error "{response.status_code}" for city: "{city}"')
            return None
    except Exception as e:
        logger.error(f'Error fetching weather data: "{e}"')
        return None


def parse_weather_data(data, target_day=0):
    if not data:
        return None
        
    city_name = data['city']['name']
    timezone_shift = int(data['city']['timezone'])

    # Восход и закат (timezone-aware)
    sunrise_utc = datetime.datetime.fromtimestamp(data['city']['sunrise'], tz=timezone.utc)
    sunset_utc = datetime.datetime.fromtimestamp(data['city']['sunset'], tz=timezone.utc)
    
    # Создаем timezone для города
    city_tz = timezone(datetime.timedelta(seconds=timezone_shift))
    
    # Конвертируем в локальное время города
    sunrise_local = sunrise_utc.astimezone(city_tz)
    sunset_local = sunset_utc.astimezone(city_tz)

    # Текущее время в UTC и городе
    now_utc = datetime.datetime.now(timezone.utc)
    now_local = now_utc.astimezone(city_tz)
    
    # Целевая дата
    target_date = (now_local + datetime.timedelta(days=target_day)).date()
    
    day_forecasts = []
    for forecast in data['list']:
        forecast_dt_utc = datetime.datetime.fromtimestamp(forecast['dt'], tz=timezone.utc)
        forecast_dt_local = forecast_dt_utc.astimezone(city_tz)
        if forecast_dt_local.date() == target_date:
            day_forecasts.append((forecast_dt_local, forecast))
    
    if not day_forecasts:
        return None
    
    # Находим текущий прогноз (ближайший к текущему времени)
    current_forecast = None
    for forecast_dt, forecast in day_forecasts:
        if forecast_dt <= now_local or not current_forecast:
            current_forecast = forecast
        else:
            break

    forecasts_by_time = {}
    for forecast_dt, forecast in day_forecasts:
        hour = forecast_dt.hour
        time_of_day = get_time_of_day(hour)

        if time_of_day not in forecasts_by_time:
            forecasts_by_time[time_of_day] = forecast
        else:
            if time_of_day == "Утром" and 8 <= hour <= 10:
                forecasts_by_time[time_of_day] = forecast
            elif time_of_day == "Днём" and 13 <= hour <= 15:
                forecasts_by_time[time_of_day] = forecast
            elif time_of_day == "Вечером" and 18 <= hour <= 20:
                forecasts_by_time[time_of_day] = forecast
            elif time_of_day == "Ночью" and (22 <= hour <= 23 or 0 <= hour <= 2):
                forecasts_by_time[time_of_day] = forecast
    
    pressure_mmhg = round(current_forecast['main']['pressure'] * 0.750062)
    if pressure_mmhg <= 750:
        pressure_status = "▽"
    elif pressure_mmhg >= 765:
        pressure_status = "△"
    else:
        pressure_status = "♢"
    
    wind_direction = get_wind_direction(current_forecast['wind']['deg'])
    wind_speed = current_forecast['wind']['speed']
    
    return {
        'date': datetime.datetime.combine(target_date, datetime.time.min),
        'city_name': city_name,
        'sunrise': sunrise_local.strftime('%H:%M'),
        'sunset': sunset_local.strftime('%H:%M'),
        'current_weather_symbol': get_weather_symbol(current_forecast['weather'][0]['id']),
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
