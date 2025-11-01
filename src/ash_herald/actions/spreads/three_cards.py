import os
import logging, time
from PIL import Image
from telebot import types
from ash_herald.actions.spreads.deck.deck import draw_cards
from ash_herald.actions.spreads.interpretation import get_interpretation
import ash_herald.utils.utils as utils

logger = logging.getLogger('THREE_CARDS')

async def three_cards(bot, call, session):
    chat_id = await utils.get_chat_id(call)
    session.state = "waiting_for_three_cards_question"

    await bot.send_message(
        chat_id, 
        "⛧ <i>Тени играют на стенах, свеча мерцает...</i>", 
        parse_mode="HTML"
    )
    time.sleep(1.5)
    await bot.send_message(
        chat_id, 
        "  ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅  \n"
        "       <i>Карты ждут твоего вопроса...</i>\n\n"
        "  <i>Какую тайну доверишь им?</i>\n"
        "⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅  ",
        parse_mode="HTML"
    )

    logger.info(f"User: {session.name}, session: waiting_for_three_cards_question")

async def handle_three_cards_question(bot, message, session):
    chat_id = await utils.get_chat_id(message)
    user_question = message.text.strip()
    deck = session.deck

    if not deck or not isinstance(deck, str):
        logger.warning(f"User: {session.name}, invalid deck: {deck}, using default 'tarot'")
        deck = 'tarot'
        session.deck = deck

    session.state = "generating_three_cards"
    session.data["user_question"] = user_question

    await bot.send_message(
        chat_id, 
        "❃ <i>Карты шелестят, переплетаясь судьбами...</i>", 
        parse_mode="HTML"
    )
    time.sleep(1.5)

    logger.info(f"User: {session.name}, action: three_cards -> draw_cards")
    cards = await draw_cards(deck, 3)
    card_lines = []
    for i, card in enumerate(cards, 1):
        position = "прямое положение" if card["position"] == "upright" else "перевёрнутое положение"
        card_line = f"✦ <b>{card['name']}</b> ⋄ <i>{position}</i>"
        card_lines.append(card_line)

    cards_text = "\n".join(card_lines)
    logger.info(f'User: {session.name}, Deck: {deck}, Question: "{utils.no_newline(user_question)}", [Cards]: {cards}')

    try:
        full_question = f"Вопрос: {user_question}. Карты: {cards}"
        logger.info(f"User: {session.name}, action: three_cards -> get_interpretation")
        meaning = await get_interpretation(full_question, cards)
        logger.info(f'User: {session.name}, meaning received: "{utils.no_newline(meaning)}"')

        session.data["previous_question"] = user_question
        session.data["previous_cards"] = cards
        session.data["previous_meaning"] = meaning
        session.state = "waiting_for_additional_question"
        
    except Exception as e:
        logger.error(f"User: {session.name}, {str(e)}")
        meaning = "<b>🜏 Символы остались безмолвны...</b> Попробуй позже."

    await bot.send_message(
        chat_id, 
        "🃍 <i>Раскрываем тайные знаки...</i>", 
        parse_mode="HTML"
    )

    message_text = (
        "<b>╔═════════✦ ⋆🃍⋆ ✦═════════╗</b>\n"
        "       <i>Три карты осветят вопрос</i>\n"
        "    <i>с разных сторон, как три свечи</i>\n"
        "  <i>— больше света, больше ясности.</i>\n"
        "<b>╚═════════✦ ⋆🃍⋆ ✦═════════╝</b>\n\n"
        f"{cards_text}\n\n"
        f"{meaning}\n\n"
        " ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ "
    )

    collage_path = await create_cards_collage(cards, deck)

    card_lines = []
    for i, card in enumerate(cards, 1):
        position = "прямое положение" if card["position"] == "upright" else "перевёрнутое положение"
        card_line = f"✦ <b>{card['name']}</b> ⋄ <i>{position}</i>"
        card_lines.append(card_line)

    cards_text = "\n".join(card_lines)
    
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("⛧ Благодарю ⛧", callback_data="thanks")
    btn2 = types.InlineKeyboardButton("🃍 Карта-пояснение 🃍", callback_data="additional_card")
    markup.add(btn1, btn2)

    try:
        if collage_path and os.path.exists(collage_path):
            with open(collage_path, "rb") as photo:
                await bot.send_photo(
                    chat_id, 
                    photo, 
                    caption=message_text, 
                    parse_mode="HTML", 
                    reply_markup=markup
                )
            os.remove(collage_path)
        else:
            await bot.send_message(chat_id, message_text, parse_mode="HTML", reply_markup=markup)
            
        logger.info(f"User: {session.name}, action: three_cards sent with clean collage")
        session.state = "waiting_for_additional_question"

    except Exception as e:
        logger.error(f"{str(e)}")
        await bot.send_message(
            chat_id, 
            "🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏"
            "       <i>Пути карт иногда извилисты,</i>\n"
            "<i>послание скрылось в тумане...</i>\n\n"
            "🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏",
            parse_mode="HTML"
        )

async def create_cards_collage(cards, deck):
    images = []
    
    for card in cards:
        card_id = card['number']
        image_path = f"src/resources/{deck}_img/{card_id}_{card['position']}.webp"
        
        if not os.path.exists(image_path):
            image_path = f"resources/tarot_img/{card_id}_{card['position']}.webp"
        
        try:
            img = Image.open(image_path)
            
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1]) 
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
                
            images.append(img)
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            continue
    
    if len(images) != 3:
        return None
    
    scale_factor = 1.4
    scaled_images = []
    for img in images:
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)
        scaled_img = img.resize((new_width, new_height), Image.LANCZOS)
        scaled_images.append(scaled_img)
    
    card_width, card_height = scaled_images[0].size
    padding = 10
    collage_width = (card_width * 3) + (padding * 4)
    collage_height = card_height + (padding * 2)
    
    collage = Image.new("RGB", (collage_width, collage_height), (255, 255, 255))
    
    for i, img in enumerate(scaled_images):
        x_position = padding + (i * (card_width + padding))
        collage.paste(img, (x_position, padding))
    
    temp_path = f"src/resources/temp_collage_{int(time.time())}.jpg"
    collage.save(temp_path, 'JPEG', quality=95)
    
    return temp_path