import time, logging

from actions.cards.deck.deck import draw_cards
from utils import texts
from utils.keyboards import cards_keyboard, cards_thanks_keyboard
from actions.cards.interpretation import get_interpretation

logger = logging.getLogger('H.cards_daily')
question = "На расклад 'Карта дня' выпала карта:"

async def cards_daily(bot, session):
    if not session.can_draw_cards_daily():
        text=(
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ 🜏 ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
            "      <i>Следующий аркан явится</i>\n"
            "   <i>после полуночи, когда старый день</i>\n"
            "<i>когда старый день уступит дорогу новому...</i>\n\n"
            "<b>Сегодняшний расклад сохраняет свою силу до конца дня.</b>\n"
        )
        logger.debug(f'"{session.username}" reached cards_daily limit for today"')
        await bot.send_message(
            session.chat_id, 
            text, 
            parse_mode="HTML", 
            reply_markup=cards_keyboard())
        return

    loading_msg1 = await bot.send_message(session.chat_id, "🕯 <i>Пламя свечи танцует в полумраке...</i>", parse_mode="HTML")
    time.sleep(1.5)

    loading_msg2 = await bot.send_message(session.chat_id, "ⴲ <i>Взгляд скользит по древним символам...</i>", parse_mode="HTML")

    cards = await draw_cards(session.deck, 1)  
    card = cards[0]
    logger.debug(f'"{session.username}", Deck: "{session.deck}", Cards: "{card['number']}": "{card['name']} - {card['position']}"') 


    card_id = card['number']
    card_name = card['name']
    card_position = "прямое положение" if card['position'] == 'upright' else "перевёрнутое положение"

    meaning = await get_interpretation(question, cards)
    logger.debug(f'"{session.username}" received cards_daily meaning: "{(meaning)}"')

    sticker_path = f"resources/{session.deck}_deck/{card_id}_{card['position']}.webp"
    try:
        with open(sticker_path, "rb") as sticker:
            await bot.send_sticker(session.chat_id, sticker)
            logger.debug(f'"{session.username}", sticker sent: "{sticker_path}"')

    except FileNotFoundError:
        logger.error(f'"{session.username}", no sticker in "{sticker_path}"')

        fallback_path = f"resources/tarot_deck/{card_id}_{card['position']}.webp"
        try:
            with open(fallback_path, "rb") as sticker:
                await bot.send_sticker(session.chat_id, sticker)
                logger.warning(f'"{session.username}", fallback sticker sent:"{fallback_path}"')
        except FileNotFoundError:
            logger.error(f'"{session.username}", no fallback sticker in "{fallback_path}"')

    try:
        card_emoji = "⛤" if card['position'] == 'upright' else "⛧"
        text = (
            f"{card_emoji} <b>{card_name}</b> ⋄ <i>{card_position}</i>\n\n"
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n\n"
            f"{meaning}")
        session.mark_cards_daily_drawn()
        try:
            await bot.delete_message(session.chat_id, loading_msg1.message_id)
            await bot.delete_message(session.chat_id, loading_msg2.message_id)
        except:
            pass

        logger.info(f'"{session.username}" received cards_daily')
        session.state = "cards_add"
        await bot.send_message(session.chat_id, text, parse_mode="HTML", reply_markup=cards_thanks_keyboard())

    except Exception as e:
        logger.error(f'"{session.username}" got error: "{str(e)}"')
        await bot.send_message(session.chat_id, text=texts.TEXT["ERROR"], parse_mode="HTML", reply_markup=cards_keyboard())