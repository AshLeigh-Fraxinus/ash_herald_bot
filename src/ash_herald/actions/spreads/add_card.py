import logging, time
from telebot import types

from ash_herald.actions.spreads.deck.deck import draw_cards
from ash_herald.actions.spreads.interpretation import get_interpretation
from ash_herald.utils import utils

logger = logging.getLogger('ADD_CARD')

async def handle_additional_question(bot, message, session):
    chat_id = await utils.get_chat_id(message)
    deck = session.deck

    if hasattr(message, 'text') and message.text:
        user_question = message.text.strip()
        session.data["additional_question"] = user_question
        question_type = "дополнительный вопрос"
        full_question_context = (
            f"Исходный вопрос: {session.data.get('previous_question', '')}. "
            f"Исходный расклад: {session.data.get('previous_cards', [])}. "
            f"Интерпретация исходного расклада: {session.data.get('previous_meaning', '')}. "
            f"Дополнительный вопрос: {user_question}. "
            "Дайте интерпретацию дополнительной карты в контексте исходного расклада и нового вопроса."
        )

    else:
        user_question = ""
        session.data["additional_question"] = ""
        question_type = "уточнение без нового вопроса"
        full_question_context = (
            f"Исходный вопрос: {session.data.get('previous_question', '')}. "
            f"Исходный расклад: {session.data.get('previous_cards', [])}. "
            f"Интерпретация исходного расклада: {session.data.get('previous_meaning', '')}. "
            "Дайте интерпретацию дополнительной карты как уточнение к исходному раскладу."
        )

    session.state = "getting additional card"

    await bot.send_message(
        chat_id, 
        "🃍 <i>Прислушиваюсь к шёпоту карт...</i> 🃍", 
        parse_mode="HTML"
    )
    time.sleep(1.5)

    logger.info(f"User: {session.name}, action: additional_card -> draw_cards, type: {question_type}")
    cards = await draw_cards(deck, 1)
    card = cards[0]

    logger.info(f"User: {session.name}, Deck: {deck}, Additional Card: {card['number']}: {card['name']} - {card['position']}")

    card_id = card['number']
    sticker_path = f"src/resources/{deck}_img/{card_id}_{card['position']}.webp"
    sticker_path = f"src/resources/{deck}_img/{card_id}_{card['position']}.webp"
    logger.info(f"Looking for sticker at: {sticker_path}")
    
    try:
        with open(sticker_path, "rb") as sticker:
            await bot.send_sticker(chat_id, sticker)
            logger.info(f"User: {session.name}, action: {sticker_path} sent")
    except FileNotFoundError:
        logger.error(f"User: {session.name}, action: no sticker in {sticker_path}")
        fallback_path = f"resources/tarot_img/{card_id}_{card['position']}.webp"
        try:
            with open(fallback_path, "rb") as sticker:
                await bot.send_sticker(chat_id, sticker)
                logger.info(f"User: {session.name}, action: fallback {fallback_path} sent")
        except FileNotFoundError:
            logger.error(f"User: {session.name}, action: no fallback sticker in {fallback_path}")
                
    position = "прямое положение" if card["position"] == "upright" else "перевёрнутое положение"
    cards_text = f"✧ <b>{card['name']}</b> ⋄ <i>{position}</i>"
    
    if user_question:
        logger.info(f'User: {session.name}, Additional Question: "{utils.no_newline(user_question)}", [Card]: {card}')
    else:
        logger.info(f'User: {session.name}, Clarification without new question, [Card]: {card}')

    try:
        full_question = full_question_context + f" Дополнительная карта: {card}."
        
        logger.info(f"User: {session.name}, action: additional_card -> get_interpretation")
        meaning = await get_interpretation(full_question, cards)
        logger.info(f'User: {session.name}, additional meaning received: "{utils.no_newline(meaning)}"')
        
    except Exception as e:
        logger.error(f"User: {session.name}, {str(e)}")
        meaning = (
            "🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏\n"
            "🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏\n"
            "       <b>Символы остались безмолвны...</b>\n"
            "<i>Попробуй позже...</i>\n"
            "🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏"
            "🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏"
        )

    if user_question:
        header = (
            "<b>╔═════════✦ ⋆🃟⋆ ✦═════════╗</b>\n"
            "         <i>Ещё один лик из тумана,</i>\n"
            "<b>╔═════════✦ ⋆🃟⋆ ✦═════════╗</b>\n"
            "         <i>Ещё один лик из тумана,</i>\n"
            "    <i>проясняющий узор судьбы...</i>\n"
            "<b>╚═════════✦ ⋆🃟⋆ ✦═════════╝</b>\n\n"
            "<b>╚═════════✦ ⋆🃟⋆ ✦═════════╝</b>\n\n"
        )
    else:
        header = (
            "<b>╔═════════✦ ⋆🃟⋆ ✦═════════╗</b>\n"
            "<b>╔═════════✦ ⋆🃟⋆ ✦═════════╗</b>\n"
            "         <i>Карта-уточнение проясняет</i>\n"
            "        <i>скрытые грани расклада...</i>\n"
            "<b>╚═════════✦ ⋆🃟⋆ ✦═════════╝</b>\n\n"
            "<b>╚═════════✦ ⋆🃟⋆ ✦═════════╝</b>\n\n"
        )

    message_text = f"{header}{cards_text}\n\n{meaning}\n⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅"
    message_text = f"{header}{cards_text}\n\n{meaning}\n⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅"
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("⛧ Благодарю ⛧", callback_data="thanks")
    btn2 = types.InlineKeyboardButton("🃍 Ещё карта-пояснение 🃍", callback_data="additional_card")
    markup.add(btn1, btn2)

    try:
        await bot.send_message(chat_id, message_text, parse_mode="HTML", reply_markup=markup)
        logger.info(f"User: {session.name}, action: additional_card sent")
        session.state = "waiting_for_additional_question"

    except Exception as e:
        logger.error(f"{str(e)}")
        await bot.send_message(
            chat_id, 
            "🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏\n"
            "🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏\n"
            "       <b>Пелена исказила послание...</b>\n"
            "<i>Пути карт иногда извилисты...</i>\n"
            "🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏", 
            "🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏", 
            parse_mode="HTML"
        )