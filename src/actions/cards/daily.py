import time
import logging

from telebot import types
from actions.cards.deck.deck import draw_cards
from actions.cards.interpretation import get_interpretation
from utils.keyboard import get_main_keyboard
from utils import utils
from utils import texts

logger = logging.getLogger('H.daily_card')
question = "На расклад 'Карта дня' выпала карта:"

async def daily_card(bot, call, session):
    chat_id = await utils.get_chat_id(call)
    
    if not session.can_draw_daily_card():
        markup = get_main_keyboard()

        await bot.send_message(
            chat_id, 
            f"{texts.DAILY_CARD_LIMIT}",
            parse_mode="HTML",
            reply_markup=markup
        )
        logger.debug(f'"{session.name}" reched daily_card limit for today"')
        return

    deck = session.deck 

    loading_msg1 = await bot.send_message(chat_id, "🕯 <i>Пламя свечи танцует в полумраке...</i>", parse_mode="HTML")
    time.sleep(1.5)

    loading_msg2 = await bot.send_message(chat_id, "ⴲ <i>Взгляд скользит по древним символам...</i>", parse_mode="HTML")

    cards = await draw_cards(deck, 1)  
    card = cards[0]
    logger.debug(f'"{session.name}", Deck: "{deck}", Cards: "{card['number']}": "{card['name']} - {card['position']}"') 

    session.mark_daily_card_drawn()

    card_id = card['number']
    card_name = card['name']
    card_position = "прямое положение" if card['position'] == 'upright' else "перевёрнутое положение"

    meaning = await get_interpretation(question, cards)
    logger.debug(f'"{session.name}" received daily_card meaning: "{utils.no_newline(meaning)}"')

    sticker_path = f"resources/{deck}_deck/{card_id}_{card['position']}.webp"
    try:
        with open(sticker_path, "rb") as sticker:
            await bot.send_sticker(chat_id, sticker)
            logger.debug(f'"{session.name}", sticker sent: "{sticker_path}"')
    except FileNotFoundError:
        logger.error(f'"{session.name}", no sticker in "{sticker_path}"')

        fallback_path = f"resources/deck_tarot/{card_id}_{card['position']}.webp"
        try:
            with open(fallback_path, "rb") as sticker:
                await bot.send_sticker(chat_id, sticker)
                logger.warning(f'"{session.name}", fallback sticker sent:"{fallback_path}"')
        except FileNotFoundError:
            logger.error(f'"{session.name}", no fallback sticker in "{fallback_path}"')

    try:
        card_emoji = "⛤" if card['position'] == 'upright' else "⛧"
        message_text = (
            f"{card_emoji} <b>{card_name}</b> ⋄ <i>{card_position}</i>\n\n"
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n\n"
            f"{meaning}")

        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("⛧ Благодарю ⛧", callback_data="thanks")
        markup.add(btn1)

        await bot.send_message(chat_id, message_text, parse_mode="HTML", reply_markup=markup)

        try:
            await bot.delete_message(chat_id, loading_msg1.message_id)
            await bot.delete_message(chat_id, loading_msg2.message_id)
        except:
            pass

        logger.info(f'"{session.name}" received daily_card')
        session.state = "waiting_for_additional_question"

    except Exception as e:
        logger.error(f'"{session.name}" got error: "{str(e)}"')
        await bot.send_message(chat_id, texts.ERROR_TEXT, parse_mode="HTML")