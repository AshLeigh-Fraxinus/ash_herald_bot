from telebot import types
from .weather_data import get_weather_symbol

def format_weather_message(data, period_name="сегодня"):
    if not data:
        return "Не удалось получить данные о погоде."

    if data['type'] == 'weekly':
        return _format_weekly(data)
    else:
        return _format_daily(data, period_name)

def _format_daily(data, period_name):
    date_str = data['date'].strftime('%d.%m')
    
    msg = (
        f"<b>════════✦ ₊ ⊹ {data['current_symbol']} ⊹ ₊ ✦════════</b>\n\n"
        f"<b>Погода в городе {data['city_name']} на {period_name} ({date_str}):</b>\n\n"
    )

    times = ['Утром', 'Днём', 'Вечером', 'Ночью']
    for t in times:
        if t in data['forecasts_by_time']:
            fc = data['forecasts_by_time'][t]
            
            symbol = get_weather_symbol(fc['weather'][0]['id'])
            temp = round(fc['main']['temp'])
            feels = round(fc['main']['feels_like'])
            desc = fc['weather'][0]['description']
            
            msg += f"✧ {t}:\n      ⋅  {symbol} {desc}\n      ⋅  {temp}°C <i>(ощущается как {feels}°C)</i>\n"

    msg += (
        f"\n"
        f"✧ Ветер: {data['wind_direction']} {data['wind_speed']} м/с\n"
        f"✧ Давление: {data['pressure_mmhg']} мм рт.ст. {data['pressure_status']}\n\n"
        f"✧ Восход солнца: {data['sunrise']}\n"
        f"✧ Закат солнца: {data['sunset']}\n"
    )
    return msg

def _format_weekly(data):
    msg = f"<b>════════✦ ₊ ⊹ 🔅 ⊹ ₊ ✦════════</b>\n\n"
    msg += f"<b>Погода в городе {data['city_name']} на 5 дней:</b>\n\n"

    weekdays = {0: "Пн", 1: "Вт", 2: "Ср", 3: "Чт", 4: "Пт", 5: "Сб", 6: "Вс"}

    for day in data['days']:
        d_str = day['date'].strftime('%d.%m')
        wd = weekdays[day['date'].weekday()]

        msg += (
            f"✧ <code>{d_str} ({wd})</code>:  {day['symbol']}\n"
            f"   ⋅ температура: от {day['temp_min']}° до {day['temp_max']}°\n"
            f"   ⋅ ветер: {day['wind_direction']} {day['wind_speed']} м/с\n"
            f"   ⋅ давление: {day['pressure_mmhg']} мм {day['pressure_status']}\n\n"
        )
    
    return msg

def create_weather_keyboard(current_view="today"):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []

    if current_view != "today":
        buttons.append(types.InlineKeyboardButton("✧ Сегодня", callback_data="weather_today"))
        
    if current_view != "tomorrow":
        buttons.append(types.InlineKeyboardButton("✧ Завтра", callback_data="weather_tomorrow"))
        
    if current_view != "week":
        buttons.append(types.InlineKeyboardButton("✧ На 5 дней", callback_data="weather_week"))
        
    buttons.append(types.InlineKeyboardButton("☰ Сменить город", callback_data="weather_city"))
    buttons.append(types.InlineKeyboardButton("К истокам ⛧", callback_data="thanks"))

    markup.add(*buttons)
    return markup