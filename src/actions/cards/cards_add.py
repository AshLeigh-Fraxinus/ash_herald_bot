import logging
from utils.keyboards import cards_add_keyboard
from actions.cards.deck.deck import draw_cards
from actions.cards.interpretation import get_interpretation

logger = logging.getLogger('H.cards_add')

async def handle_additional_question(bot, session, event):
    if event and not event.startswith("cards_"):

        user_question = event.strip()
        session.temp_data["additional_question"] = user_question
        full_question_context = (
            f"Исходный вопрос: {session.temp_data.get('previous_question', '')}. "
            f"Исходный расклад: {session.temp_data.get('previous_cards', [])}. "
            f"Интерпретация исходного расклада: {session.temp_data.get('previous_meaning', '')}. "
            f"Дополнительный вопрос: {user_question}. "
            "Дай интерпретацию дополнительной карты в контексте исходного расклада и нового вопроса."
        )

    else:
        user_question = ""
        session.temp_data["additional_question"] = ""
        full_question_context = (
            f"Исходный вопрос: {session.temp_data.get('previous_question', '')}. "
            f"Исходный расклад: {session.temp_data.get('previous_cards', [])}. "
            f"Интерпретация исходного расклада: {session.temp_data.get('previous_meaning', '')}. "
            "Дай интерпретацию дополнительной карты как уточнение к исходному раскладу."
        )

    await bot.send_message(
        session.chat_id, 
        "🃍 <i>Прислушиваюсь к шёпоту карт...</i> 🃍", 
        parse_mode="HTML"
    )

    cards = await draw_cards(session.deck, 1)
    card = cards[0]

    logger.debug(f'"{session.username}", Deck: "{session.deck}", Additional Card: "{card['number']}": "{card['name']} - {card['position']}"')

    card_id = card['number']
    sticker_path = f"resources/{session.deck}_deck/{card_id}_{card['position']}.webp"
    fallback_path = f"resources/tarot_deck/{card_id}_{card['position']}.webp"
    
    try:
        with open(sticker_path, "rb") as sticker:
            await bot.send_sticker(session.chat_id, sticker)
            logger.info(f'"{session.username}", "{sticker_path}" sent')

    except FileNotFoundError:
        logger.error(f'"{session.username}", got error: no sticker in "{sticker_path}"')
        try:
            with open(fallback_path, "rb") as sticker:
                await bot.send_sticker(session.chat_id, sticker)
                logger.warning(f'"{session.username}", fallback {fallback_path} sent"')

        except FileNotFoundError:
            logger.error(f'"{session.username}", no fallback sticker in {fallback_path}"')
                
    position = "прямое положение" if card["position"] == "upright" else "перевёрнутое положение"
    card_emoji = "⛤" if card['position'] == 'upright' else "⛧"
    cards_text = f"{card_emoji} <b>{card['name']}</b> ⋄ <i>{position}</i>"
    
    if user_question:
        logger.debug(f'"{session.username}", Additional Question: "{(user_question)}", [Card]: "{card}"')
    else:
        logger.debug(f'"{session.username}", Clarification without new question, [Card]: "{card}"')

    try:
        full_question = full_question_context + f" Дополнительная карта: {card}."
        meaning = await get_interpretation(full_question, cards)
        logger.debug(f'"{session.username}", additional meaning received: "{(meaning)}"')
        
    except Exception as e:
        logger.error(f'"{session.username}" got error: "{str(e)}"')
        meaning = (
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ 🜏 ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
            "       <b>Символы остались безмолвны...</b>\n"
            "<i>Попробуй позже...</i>\n"
        )

    session.state = "cards_add"
    logger.info(f'"{session.username}" received "cards_add"')
    text = f"{cards_text}\n\n{meaning}\n\n⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ "
    await bot.send_message(
        session.chat_id,
        text,
        parse_mode="HTML",
        reply_markup=cards_add_keyboard()
    )
