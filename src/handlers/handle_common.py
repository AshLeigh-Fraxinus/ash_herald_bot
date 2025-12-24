
import os, logging

from utils import texts
from utils.keyboards import main_keyboard

logger = logging.getLogger('H.handle_common')

COMMON_STATES = {
    'support': lambda bot, session, event: handle_support_message(bot, session, event)
    }

COMMON_COMMANDS = {
    'start': lambda bot, session, event: handle_start(bot, session),
    'thanks': lambda bot, session, event: handle_thanks(bot, session),
    'support': lambda bot, session, event: handle_support(bot, session, event)
}

async def handle_common(bot, session, event):
    try:
        for prefix, handler in COMMON_STATES.items():
            if session.state.startswith(prefix):
                await handler(bot, session, event)
                return
            
        for prefix, handler in COMMON_COMMANDS.items():
            if event.startswith(prefix):
                await handler(bot, session, event)
                return
            
        logger.warning(f'Unknown callback data: "{event}" from "{session.username}" in "{session.state}"')
        await handle_unknown_command(bot, session)
            
    except Exception as e:
        logger.error(f'Error handling message "{event}" for "{session.username}" in "{session.state}": {e}')
        await handle_unknown_command(bot, session)

async def handle_start(bot, session):
    session.reset_state()
    session.update_activity()
    logger.debug(f'"{session.username}" moved to "{session.state}"')

    name = session.name or session.first_name or session.username
    await bot.send_message(
        session.chat_id,
        text=texts.TEXTS["START"](name),
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

async def handle_thanks(bot, session):
    session.reset_state()
    session.update_activity()
    name = session.name or session.first_name or session.username

    await bot.send_message(
        session.chat_id,
        text=texts.TEXTS["THANKS"](name),
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

async def handle_unknown_command(bot, session):
    await bot.send_message(
        session.chat_id,
        text=texts.TEXTS["UNKNOWN"],
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

async def handle_support(bot, session, event):
    if session.state == "support":
        await handle_support_message(bot, session, event)
    else:
        session.state = "support"
        await bot.send_message(
            session.chat_id,
            text=texts.TEXTS["SUPPORT_REQUEST"],
            parse_mode="HTML"
        )
        logger.debug(f'"{session.username}" asked for support')

async def handle_support_message(bot, session, event):
    session.reset_state()
    session.update_activity()

    ADMIN = os.getenv("ADMIN")
    username = session.username or "Unknown"
    await bot.send_message(
        ADMIN,
        text=texts.TEXTS["SUPPORT_SENT_ADMIN"](username=username, event=event),
        parse_mode="HTML"
    )
    logger.debug(f'"{session.username}" message to master was sent')

    await bot.send_message(
        session.chat_id,
        text=texts.TEXTS["SUPPORT_SENT_USER"],
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

