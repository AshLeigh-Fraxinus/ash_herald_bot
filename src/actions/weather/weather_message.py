from telebot import types
from .weather_data import get_weather_symbol

def format_weather_message(weather_data, period="today"):
    if not weather_data:
        return None
        
    day_names = {"today": "сегодня", "tomorrow": "завтра"}
    date_str = weather_data['date'].strftime('%d.%m')
    
    message_text = (
        f"<b>════════✦ ₊ ⊹ {weather_data['current_weather_symbol']} ₊ ⊹ ✦════════</b>\n\n"
        f"<b>Погода в городе {weather_data['city_name']} на {day_names[period]} ({date_str}):</b>\n\n"
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
            
            message_text += f"✧ {time}:\n      ⋅  {symbol} {description}\n      ⋅  {temp}°C <i>(ощущается как {feels_like}°C)</i>\n"

    message_text += (
        f"\n"
        f"✧ Ветер: {weather_data['wind_direction']} {weather_data['wind_speed']} м/с\n"
        f"✧ Давление: {weather_data['pressure_mmhg']} мм рт.ст. {weather_data['pressure_status']}\n\n"
        f"✧ Восход солнца: {weather_data['sunrise']}\n"
        f"✧ Закат солнца: {weather_data['sunset']}\n"
    )
    return message_text

def create_weather_keyboard(include_weather_city=True, include_tomorrow=True):
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    buttons = []
    if include_tomorrow:
        buttons.append(types.InlineKeyboardButton("Прогноз на завтра", callback_data="weather_tomorrow"))
    if include_weather_city:
        buttons.append(types.InlineKeyboardButton("☰ Сменить город", callback_data="weather_city"))
    buttons.append(types.InlineKeyboardButton("⛧ К истокам", callback_data="thanks"))

    for i in range(0, len(buttons), 2):
        row = buttons[i:i+2]
        markup.add(*row)
        
    return markup