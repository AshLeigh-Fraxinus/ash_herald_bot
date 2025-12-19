import logging
from utils import texts

from service.sessions import session_manager
from actions.cards.cards_daily import cards_daily
from actions.cards.cards_add import handle_additional_question
from actions.settings.change_deck import change_deck, get_deck_display, request_deck
from actions.cards.cards_three import handle_cards_three_question, cards_three
from utils.keyboards import cards_keyboard

logger = logging.getLogger('H.handle_cards')

CARD_STATES = {
    'cards_three_question': lambda bot, session, event: handle_cards_three_question(bot, session, event),
    'cards_daily': lambda bot, session, event: handle_additional_question(bot, session, event),
    'cards_three': lambda bot, session, event: handle_additional_question(bot, session, event),
    'cards_add': lambda bot, session, event: handle_additional_question(bot, session, event),
    }

CARD_COMMANDS = {
    'cards_menu': lambda bot, session, event: handle_cards_menu(bot, session),
    'cards_daily': lambda bot, session, event: cards_daily(bot, session),
    'cards_three': lambda bot, session, event: cards_three(bot, session),
    'cards_deck': lambda bot, session, event: request_deck(bot, session),
    'cards_add': lambda bot, session, event: handle_additional_question(bot, session, event),
    'deck_': lambda bot, session, event: handle_change_deck(bot, session, event),
}

async def handle_cards(bot, session, event):
    try:
        for prefix, handler in CARD_STATES.items():
            if session.state.startswith(prefix):
                await handler(bot, session, event)
                return

        for prefix, handler in CARD_COMMANDS.items():
            if event.startswith(prefix):
                await handler(bot, session, event)
                return

        logger.warning(f'Unknown callback data: "{event}" from "{session.username}" in "{session.state}"')
        await handle_unknown_command(bot, session)

    except Exception as e:
        logger.error(f'Error handling callback "{event}" for "{session.username}" in "{session.state}": {e}')
        await handle_unknown_command(bot, session)

async def handle_cards_menu(bot, session):
    session.state = "cards_menu"
    logger.debug(f'"{session.username}" prefer "{session.deck}"')
    deck_name = get_deck_display(session)
    await bot.send_message(
        session.chat_id,
        text = texts.TEXTS["CARDS_MENU"](deck_name),
        parse_mode="HTML",
        reply_markup=cards_keyboard()
    )

async def handle_change_deck(bot, session, event):
    await change_deck(bot, session, event)
    session_manager.save_session(session.chat_id)
    logger.debug(f'"{session.username}" prefer "{session.deck}"')
    await handle_cards_menu(bot, session)

async def handle_unknown_command(bot, session):
    await bot.send_message(
        session.chat_id,
        text=texts.TEXTS["UNKNOWN"],
        parse_mode="HTML",
        reply_markup=cards_keyboard()
    )

