from telebot import types

def main_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="🂠 Обратиться к картам", callback_data='cards_menu')
    btn2 = types.InlineKeyboardButton(text="☽ Лунные знамения", callback_data='moon_day')
    btn3 = types.InlineKeyboardButton(text="✧ Погодные знамения", callback_data='weather_menu')
    btn4 = types.InlineKeyboardButton(text="☰ Святилище настроек", callback_data='change_menu')
    btn5 = types.InlineKeyboardButton(text="✲ Сообщить об ошибке", callback_data='support')
    markup.add(btn2, btn1)
    markup.add(btn3, btn4)
    markup.add(btn5)
    return markup

def thanks_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("⛧ К истокам", callback_data="thanks")
    markup.add(btn1)
    return markup


def cards_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="✧ Карта дня", callback_data='cards_daily')
    btn2 = types.InlineKeyboardButton(text="✧ Три лика судьбы", callback_data='cards_three')
    btn3 = types.InlineKeyboardButton(text="🂠 Выбрать колоду", callback_data='cards_deck')
    btn4 = types.InlineKeyboardButton(text="⛧ К истокам⛧ ", callback_data='thanks')
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3, btn4)
    return markup

def cards_add_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🃍 Ещё карта-пояснение 🃍", callback_data="cards_add")
    btn2 = types.InlineKeyboardButton("⛧ К раскладам", callback_data="cards_menu")
    btn3 = types.InlineKeyboardButton("К истокам ⛧", callback_data="thanks")
    markup.add(btn1)
    markup.add(btn2, btn3)
    return markup

def cards_thanks_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("⛧ К раскладам", callback_data="cards_menu")
    btn2 = types.InlineKeyboardButton("К истокам ⛧", callback_data="thanks")
    markup.add(btn1, btn2)
    return markup

def settings_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="✧ Изменить имя", callback_data='change_name')
    btn2 = types.InlineKeyboardButton(text="🂠 Выбрать колоду", callback_data='change_deck')
    btn3 = types.InlineKeyboardButton(text="☰ Выбрать город", callback_data='change_city')
    btn4 = types.InlineKeyboardButton(text="⛧ К истокам ⛧", callback_data='thanks')
    markup.add(btn2, btn3)
    markup.add(btn1, btn4)
    return markup

def weather_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="✧ Погода сегодня", callback_data='weather_today')
    btn2 = types.InlineKeyboardButton(text="✧ Погода завтра", callback_data='weather_tomorrow')
    btn3 = types.InlineKeyboardButton(text="☰ Выбрать город", callback_data='weather_city')
    btn4 = types.InlineKeyboardButton(text="⛧ К истокам ⛧", callback_data='thanks')
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup

def weather_thanks_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("☰ Сменить город", callback_data="weather_city")
    btn2 = types.InlineKeyboardButton("⛧ К погоде", callback_data="weather_menu")
    btn3 = types.InlineKeyboardButton("К истокам ⛧", callback_data="thanks")
    markup.add(btn1)
    markup.add(btn2, btn3)
    return markup
