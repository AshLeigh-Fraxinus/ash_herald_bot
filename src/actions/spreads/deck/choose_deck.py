import logging
import utils.utils as utils
import utils.keyboard as keyboard

logger = logging.getLogger('CHOOSE_DECK')

async def choose_deck(bot, call, session):
    chat_id = await utils.get_chat_id(call)
    session.state = "choosing_deck"

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text="<i>На какую колоду падает твой взгляд?</i>\n",
        parse_mode="HTML",
        reply_markup=keyboard.get_deck_keyboard()
    )

async def def_deck(bot, call, session):
    chat_id = await utils.get_chat_id(call)
    
    try:
        deck_display = ""
        if call.data in ('tarot_deck', '/tarot_deck'):
            session.deck = 'tarot'
            deck_display = "Таро"
            logger.info(f"User: {session.name}, deck set to: tarot")

        elif call.data in ('deviant_moon_deck', '/deviant_moon_deck'):
            session.deck = 'deviant_moon'
            deck_display = "Безумной луны"
            logger.info(f"User: {session.name}, deck set to: deviant")

        elif call.data in ('santa_muerte_deck', '/santa_muerte_deck'):
            session.deck = 'santa_muerte'
            deck_display = "Святой смерти"
            logger.info(f"User: {session.name}, deck set to: muerte")

        elif call.data in ('lenorman_deck', '/lenorman_deck'):
            session.deck = 'lenorman'
            deck_display = "Ленорман"
            logger.info(f"User: {session.name}, deck set to: lenorman")

        elif call.data in ('persona3_deck', '/persona3_deck'):
            session.deck = 'persona3'
            deck_display = "Персона 3"
            logger.info(f"User: {session.name}, deck set to: persona3")
        else:
            logger.warning(f"User: {session.name}, unknown deck selection: {call.data}")
            await bot.send_message(
                chat_id,
                "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ 🜏 ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
                "☤ Тени шепчут, что этот путь пока закрыт...,</b>\n"
                "Выбери из предложенных колод.\n",
                parse_mode="HTML")
            return
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ 🃍 ⋅ ⋆ ⋅ ✦ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
                 f"<i>В бархате ночи лежит колода {deck_display},</i>\n"
                 f"<i>каждая карта — врата в миры...</i>\n\n"
                 f"         <i>Чьи голоса услышишь сегодня?</i>\n",
            parse_mode="HTML",
            reply_markup=keyboard.get_cards_keyboard()
        )

    except Exception as e:
        logger.error(f"User: {session.name}, error in def_deck: {e}")
        await bot.send_message(
            chat_id,
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ 🜏 ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
            "       <b>Пелена тумана сокрыла ответ...,\n"
            "Древние силы временно безмолвствуют. Попробуй снова...",
            parse_mode="HTML")