import logging
import ash_herald.utils.utils as utils
import ash_herald.utils.keyboard as keyboard

logger = logging.getLogger('CHOOSE_DECK')

async def choose_deck(bot, call, session):
    chat_id = await utils.get_chat_id(call)
    session.state = "choosing_deck"
    session.deck = 'tarot'

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text="<i>На какую колоду падает твой взгляд?</i>\n",
        parse_mode="HTML",
        reply_markup=keyboard.get_deck_keyboard()
    )

    logger.info(f"User: {session.name}, session: choosing_deck")

async def def_deck(bot, call, session):
    chat_id = await utils.get_chat_id(call)
    
    try:
        deck_display = ""
        if call.data in ('tarot_deck', '/tarot_deck'):
            session.deck = 'tarot'
            deck_display = "Таро"
            logger.debug(f"User: {session.name}, deck selected: tarot")

        elif call.data in ('deviant_deck', '/deviant_deck'):
            session.deck = 'deviant'
            deck_display = "Безумной луны"
            logger.debug(f"User: {session.name}, deck selected: deviant")

        elif call.data in ('muerte_deck', '/muerte_deck'):
            session.deck = 'muerte'
            deck_display = "Святой смерти"
            logger.debug(f"User: {session.name}, deck selected: muerte")

        elif call.data in ('lenorman_deck', '/lenorman_deck'):
            session.deck = 'lenorman'
            deck_display = "Ленорман"
            logger.debug(f"User: {session.name}, deck selected: lenorman")
        else:
            logger.warning(f"User: {session.name}, unknown deck selection: {call.data}")
            await bot.send_message(
                chat_id,
                "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ 🜏 ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
                "☤ Тени шепчут, что этот путь пока закрыт...,</b>\n"
                "Выбери из предложенных колод.\n",
                parse_mode="HTML")
            return

        logger.info(f"User: {session.name}, deck set to: {session.deck}")
        
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