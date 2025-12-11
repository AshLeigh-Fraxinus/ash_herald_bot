import logging, time
from telebot import types

from actions.cards.deck.deck import draw_cards
from actions.cards.interpretation import get_interpretation
from utils import utils

logger = logging.getLogger('H.add_card')

async def handle_additional_question(bot, message, session):
    chat_id = await utils.get_chat_id(message)
    deck = session.deck

    if hasattr(message, 'text') and message.text:
        user_question = message.text.strip()
        session.temp_data["additional_question"] = user_question
        full_question_context = (
            f"Исходный вопрос: {session.temp_data.get('previous_question', '')}. "
            f"Исходный расклад: {session.temp_data.get('previous_cards', [])}. "
            f"Интерпретация исходного расклада: {session.temp_data.get('previous_meaning', '')}. "
            f"Дополнительный вопрос: {user_question}. "
            "Дайте интерпретацию дополнительной карты в контексте исходного расклада и нового вопроса."
        )

    else:
        user_question = ""
        session.temp_data["additional_question"] = ""
        full_question_context = (
            f"Исходный вопрос: {session.temp_data.get('previous_question', '')}. "
            f"Исходный расклад: {session.temp_data.get('previous_cards', [])}. "
            f"Интерпретация исходного расклада: {session.temp_data.get('previous_meaning', '')}. "
            "Дайте интерпретацию дополнительной карты как уточнение к исходному раскладу."
        )

    session.state = "getting additional card"

    await bot.send_message(
        chat_id, 
        "🃍 <i>Прислушиваюсь к шёпоту карт...</i> 🃍", 
        parse_mode="HTML"
    )
    time.sleep(1.5)

    cards = await draw_cards(deck, 1)
    card = cards[0]

    logger.debug(f'"{session.name}", Deck: "{deck}", Additional Card: "{card['number']}": "{card['name']} - {card['position']}"')

    card_id = card['number']
    sticker_path = f"resources/{deck}_deck/{card_id}_{card['position']}.webp"
    sticker_path = f"resources/{deck}_deck/{card_id}_{card['position']}.webp"
    
    try:
        with open(sticker_path, "rb") as sticker:
            await bot.send_sticker(chat_id, sticker)
            logger.info(f'"{session.name}", "{sticker_path}" sent')
    except FileNotFoundError:
        logger.error(f'"{session.name}", got error: no sticker in "{sticker_path}"')
        fallback_path = f"resources/deck_tarot/{card_id}_{card['position']}.webp"
        try:
            with open(fallback_path, "rb") as sticker:
                await bot.send_sticker(chat_id, sticker)
                logger.warning(f'"{session.name}", fallback {fallback_path} sent"')
        except FileNotFoundError:
            logger.error(f'"{session.name}", no fallback sticker in {fallback_path}"')
                
    position = "прямое положение" if card["position"] == "upright" else "перевёрнутое положение"
    card_emoji = "⛤" if card['position'] == 'upright' else "⛧"
    cards_text = f"{card_emoji} <b>{card['name']}</b> ⋄ <i>{position}</i>"
    
    if user_question:
        logger.debug(f'"{session.name}", Additional Question: "{utils.no_newline(user_question)}", [Card]: "{card}"')
    else:
        logger.debug(f'"{session.name}", Clarification without new question, [Card]: "{card}"')

    try:
        full_question = full_question_context + f" Дополнительная карта: {card}."

        meaning = await get_interpretation(full_question, cards)
        logger.debug(f'"{session.name}", additional meaning received: "{utils.no_newline(meaning)}"')
        
    except Exception as e:
        logger.error(f'"{session.name}" got error: "{str(e)}"')
        meaning = (
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ 🜏 ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
            "       <b>Символы остались безмолвны...</b>\n"
            "<i>Попробуй позже...</i>\n"
        )

    message_text = f"{cards_text}\n\n{meaning}\n\n⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ "
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("⛧ Благодарю ⛧", callback_data="thanks")
    btn2 = types.InlineKeyboardButton("🃍 Ещё карта-пояснение 🃍", callback_data="additional_card")
    markup.add(btn1, btn2)

    try:
        await bot.send_message(chat_id, message_text, parse_mode="HTML", reply_markup=markup)
        logger.info(f'"{session.name}" received "additional_card"')
        session.state = "waiting_for_additional_question"

    except Exception as e:
        logger.error(f"{str(e)}")
        await bot.send_message(
            chat_id, 
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ 🜏 ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
            "       <b>Пелена исказила послание...</b>\n"
            "<i>Пути карт иногда извилисты...</i>\n",
            parse_mode="HTML"
        )