import logging
from telebot import types

from ash_herald.actions.spreads import daily_card, three_cards
from ash_herald.actions.spreads.add_card import handle_additional_question
from ash_herald.actions.spreads.deck import choose_deck
from ash_herald import sessions, texts
from ash_herald.utils import keyboard, utils

logger = logging.getLogger('SPREADS_HANDLER')

#------------------
# Обработка /cards_spread
#------------------
async def handle_spread(bot, message):
    chat_id = await utils.get_chat_id(message)
    name_tuple = utils.get_username_and_names(message)
    name = sessions.session_manager.get_name(chat_id, name_tuple)
    session = sessions.session_manager.get_session(chat_id, name)
    logger.info(f"User: {session.name}, action: /cards_spread")
    sessions.session_manager.reset_session(chat_id)
    await bot.send_message(chat_id, texts.CARDS_TEXT, parse_mode="HTML", reply_markup=keyboard.get_cards_keyboard())

#---------------------
# Обработка 'Спасибо'
#---------------------
async def handle_thanks(bot, obj, session=None):
    chat_id = await utils.get_chat_id(obj)
    if session is None:
        name_tuple = utils.get_username_and_names(obj)
        name = sessions.session_manager.get_name(chat_id, name_tuple)
        session = sessions.session_manager.get_session(chat_id, name)
    
    logger.info(f"-> SPREADS_HANDLER, User: {session.name}, returning to main menu")
    
    sessions.session_manager.reset_session(chat_id)
    await bot.send_message(chat_id, texts.THANKS_TEXT, parse_mode="HTML", reply_markup=keyboard.get_main_keyboard())

async def handle_daily_card_text(bot, message, session):
    await daily_card.daily_card(bot, message, session)

async def handle_three_cards_text(bot, message, session):
    await three_cards.three_cards(bot, message, session)

async def handle_cards_spread_text(bot, message, session):
    await handle_spread(bot, message)

text_handlers = {
    "daily_card": handle_daily_card_text,
    "three_cards": handle_three_cards_text,
    "cards_spread": handle_cards_spread_text,
    "✧ карта дня": handle_daily_card_text,
    "✦ три лика судьбы": handle_three_cards_text,
    "✥ выбрать колоду": lambda bot, message, session: choose_deck.choose_deck(bot, message, session)
}

async def handle_daily_card_callback(bot, call, session):
    await daily_card.daily_card(bot, call, session)

async def handle_three_cards_callback(bot, call, session):
    await three_cards.three_cards(bot, call, session)

async def handle_choose_deck_callback(bot, call, session):
    await choose_deck.choose_deck(bot, call, session)

async def handle_deck_selection_callback(bot, call, session):
    await choose_deck.def_deck(bot, call, session)

callback_handlers = {
    "daily_card": handle_daily_card_callback,
    "three_cards": handle_three_cards_callback,
    "additional_card": handle_additional_question,
    "choose_deck": handle_choose_deck_callback,
    'tarot_deck': handle_deck_selection_callback,
    'deviant_deck': handle_deck_selection_callback,
    'muerte_deck': handle_deck_selection_callback,
    'lenorman_deck': handle_deck_selection_callback,
    "thanks": handle_thanks
}

async def handle_spread_message(bot, message, session):
    text = message.text.strip().lower()
    
    if text in text_handlers:
        await text_handlers[text](bot, message, session)
        return True
        
    for key in text_handlers:
        if key in text:
            await text_handlers[key](bot, message, session)
            return True
            
    return False

async def handle_spread_callback(bot, call, session):
    logger.info(f"-> SPREADS_HANDLER, User: {session.name}, action: {call.data}")

    if call.data in callback_handlers:
        await callback_handlers[call.data](bot, call, session)
        return True
        
    return False

async def handle_spread_waiting_state(bot, message, session):
    if session.state == "waiting_for_three_cards_question":
        await three_cards.handle_three_cards_question(bot, message, session)
        return True
    
    elif session.state == "waiting_for_additional_question":
        await handle_additional_question(bot, message, session)
        return True
    
    elif session.state == "choosing_deck" and hasattr(message, 'text'):
        await choose_deck.def_deck(bot, message, session)
        return True
    
    return False