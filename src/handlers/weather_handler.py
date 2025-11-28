from .section_handler import SectionHandler
from actions.weather.weather_actions import weather_today, weather_tomorrow, change_city

class WeatherHandler(SectionHandler):
    def __init__(self):
        super().__init__()
        self.commands = {
            "weather_today": weather_today,
            "change_city": weather_today,
        }
        
        self.callbacks = {
            "change_city": change_city,
            "weather_today": weather_today,
            "weather_tomorrow": weather_tomorrow,
        }