import os, logging
from telebot import types
from service.sessions import session_manager

logger = logging.getLogger('H.change_deck')

async def request_deck(bot, session):
    await bot.send_message(
        session.chat_id,
        text="<i>На какую колоду падает твой взгляд?</i>\n",
        parse_mode="HTML",
        reply_markup=deck_keyboard()
    )

async def change_deck(bot, session, event):
    session.deck = event.replace('deck_', '')
    deck_folder = f"resources/{session.deck}_deck/"
    
    if os.path.exists(deck_folder) and os.path.isdir(deck_folder):
        logger.info(f'"{session.username}" set deck: "{session.deck}"')
        deck_name = get_deck_display(session)
        await bot.send_message(
            session.chat_id,
            f'<i>Выбрана колода "{deck_name}"</i>', parse_mode="HTML"
        )
        return
    
    else:
        logger.warning(f'"{session.username}"selected unknown deck: "{event}"')
        await bot.send_message(
            session.chat_id,
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ 🜏 ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
            "☤ Этот путь пока закрыт...,</b>\n"
            "Выбери из предложенных колод.\n",
            parse_mode="HTML",
            reply_markup=deck_keyboard())
    return

def get_deck_display(session):
    if session.deck == 'tarot': deck_display = "Таро"
    if session.deck == 'deviant_moon': deck_display = "Безумной луны"
    if session.deck == 'santa_muerte': deck_display = "Святой смерти"
    if session.deck == 'lenorman': deck_display = "Ленорман"
    if session.deck == 'persona3': deck_display = "Персона 3"
    return deck_display

def deck_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="✧ Классическое Таро", callback_data='deck_tarot')
    btn2 = types.InlineKeyboardButton(text="✧ Таро Безумной Луны", callback_data='deck_deviant_moon')
    btn3 = types.InlineKeyboardButton(text="✧ Таро Святой Смерти", callback_data='deck_santa_muerte')
    btn4 = types.InlineKeyboardButton(text="✧ Персона 3", callback_data='deck_persona3')
    btn5 = types.InlineKeyboardButton(text="✦ Оракул Ленорман", callback_data='deck_lenorman')
    btn6 = types.InlineKeyboardButton(text="⛧ Обернуться", callback_data='cards_menu')
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4, btn5)
    markup.add(btn6)
    return markup