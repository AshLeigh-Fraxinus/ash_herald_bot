import os
import requests
import logging
from datetime import datetime, timedelta, timezone
from collections import defaultdict

logger = logging.getLogger('H.weather_service')

def get_weather_data(city):
    base_url = os.getenv("WEATHER_API_URL")
    key = os.getenv("WEATHER_API_KEY")
    url = f"{base_url}{city}&cnt=40&appid={key}&units=metric&lang=ru"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        logger.error(f'API error "{response.status_code}" for city: "{city}"')
        return None
    except Exception as e:
        logger.error(f'Error fetching weather data: "{e}"')
        return None

class WeatherParser:
    def __init__(self, data):
        self.data = data
        self.city_name = data['city']['name']
        self.tz_shift = int(data['city']['timezone'])
        self.city_tz = timezone(timedelta(seconds=self.tz_shift))
        self.now_utc = datetime.now(timezone.utc)
        self.now_local = self.now_utc.astimezone(self.city_tz)
        self._grouped = self._group_by_day()

    def _group_by_day(self):
        grouped = defaultdict(list)
        for item in self.data['list']:
            dt_utc = datetime.fromtimestamp(item['dt'], tz=timezone.utc)
            dt_local = dt_utc.astimezone(self.city_tz)
            grouped[dt_local.date()].append({
                'dt': dt_local,
                'data': item
            })
        return grouped

    def get_day_report(self, day_offset=0):
        target_date = (self.now_local + timedelta(days=day_offset)).date()
        day_items = self._grouped.get(target_date)
        if not day_items: return None

        sunrise = datetime.fromtimestamp(self.data['city']['sunrise'], tz=timezone.utc).astimezone(self.city_tz)
        sunset = datetime.fromtimestamp(self.data['city']['sunset'], tz=timezone.utc).astimezone(self.city_tz)

        current_item = day_items[0]['data']
        for item in day_items:
            if item['dt'] > self.now_local:
                current_item = item['data']
                break

        forecasts_by_time = {}
        for item in day_items:
            hour = item['dt'].hour
            phase = self._get_time_of_day(hour)
            if phase not in forecasts_by_time:
                 forecasts_by_time[phase] = item['data']
            else:
                if (phase == "Утром" and 8 <= hour <= 10) or \
                   (phase == "Днём" and 13 <= hour <= 15) or \
                   (phase == "Вечером" and 18 <= hour <= 20):
                    forecasts_by_time[phase] = item['data']

        pressure_val = round(current_item['main']['pressure'] * 0.750062)
        
        return {
            'type': 'daily',
            'city_name': self.city_name,
            'date': target_date,
            'sunrise': sunrise.strftime('%H:%M'),
            'sunset': sunset.strftime('%H:%M'),
            'current_symbol': get_weather_symbol(current_item['weather'][0]['id']),
            'forecasts_by_time': forecasts_by_time,
            'pressure_mmhg': pressure_val,
            'pressure_status': self._get_pressure_status(pressure_val),
            'wind_speed': current_item['wind']['speed'],
            'wind_direction': self._get_wind_direction(current_item['wind']['deg'])
        }

    def get_week_report(self):
        days_data = []
        for date, items in sorted(self._grouped.items()):
            temps = [x['data']['main']['temp'] for x in items]

            noon_item = next((x['data'] for x in items if 12 <= x['dt'].hour <= 15), items[len(items)//2]['data'])

            pressure_val = round(noon_item['main']['pressure'] * 0.750062)

            days_data.append({
                'date': date,
                'temp_min': round(min(temps)),
                'temp_max': round(max(temps)),
                'symbol': get_weather_symbol(noon_item['weather'][0]['id']),

                'wind_speed': round(noon_item['wind']['speed'], 1),
                'wind_direction': self._get_wind_direction(noon_item['wind']['deg']),
                'pressure_mmhg': pressure_val,
                'pressure_status': self._get_pressure_status(pressure_val)
            })
        
        return {
            'type': 'weekly',
            'city_name': self.city_name,
            'days': days_data
        }

    @staticmethod
    def _get_time_of_day(hour):
        if 6 <= hour < 12: return "Утром"
        elif 12 <= hour < 18: return "Днём"
        elif 18 <= hour < 24: return "Вечером"
        else: return "Ночью"

    @staticmethod
    def _get_pressure_status(mmhg):
        if mmhg <= 750: return "▽"
        elif mmhg >= 765: return "△"
        return "♢"

    @staticmethod
    def _get_wind_direction(degrees):
        directions = [
            (0, 22.5, "северный"), (22.5, 67.5, "с-в"),
            (67.5, 112.5, "восточный"), (112.5, 157.5, "ю-в"),
            (157.5, 202.5, "южный"), (202.5, 247.5, "ю-з"),
            (247.5, 292.5, "западный"), (292.5, 337.5, "с-з"),
            (337.5, 360, "северный")
        ]
        for min_d, max_d, name in directions:
            if min_d <= degrees < max_d: return name
        return "сев"

def get_weather_symbol(code):
    SYMBOLS = {
        "⛈️": [200, 201, 202, 210, 211, 212, 221, 230, 231, 232],
        "🌧️": [500, 501, 502, 503, 504, 511, 520, 521, 522, 531],
        "🌨️": [600, 601, 602, 611, 612, 613, 615, 616, 620, 621, 622],
        "☁️": [741, 804],
        "☀️": [800], "⛅": [801, 802], "🌥️": [803, 804]
    }
    for symbol, codes in SYMBOLS.items():
        if code in codes: return symbol
    return "🌤"