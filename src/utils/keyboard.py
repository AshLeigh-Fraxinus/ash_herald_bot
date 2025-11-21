from telebot import types

def get_main_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="🂠 Обратиться к картам", callback_data='cards_spread')
    btn2 = types.InlineKeyboardButton(text="☽ Обратиться к луне", callback_data='moon_day')
    markup.add(btn1)
    markup.add(btn2)
    return markup

def get_cards_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="✧ Карта дня", callback_data='daily_card')
    btn2 = types.InlineKeyboardButton(text="✧ Три лика судьбы", callback_data='three_cards')
    btn3 = types.InlineKeyboardButton(text="✥ Выбрать колоду", callback_data='choose_deck')
    btn4 = types.InlineKeyboardButton(text="⛧ К истокам", callback_data='thanks')
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)
    return markup

def get_deck_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="✧ Классическое Таро", callback_data='tarot_deck')
    btn2 = types.InlineKeyboardButton(text="✧ Таро Безумной Луны", callback_data='deviant_moon_deck')
    btn3 = types.InlineKeyboardButton(text="✧ Таро Святой Смерти", callback_data='santa_muerte_deck')
    btn4 = types.InlineKeyboardButton(text="✧ Персона 3", callback_data='persona3_deck')
    btn5 = types.InlineKeyboardButton(text="✦ Оракул Ленорман", callback_data='lenorman_deck')
    btn6 = types.InlineKeyboardButton(text="⛧ Обернуться", callback_data='cards_spread')
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)
    markup.add(btn5)
    markup.add(btn6)
    return markup
