import logging
from service.sessions import session_manager

logger = logging.getLogger('H.change_name')

async def request_name(bot, session):
    session.state = "change_name"
    await bot.send_message(
        session.chat_id,
        text=("<i>Как мне к тебе обращаться?</i>\n"),
        parse_mode="HTML"
    )

async def change_name(bot, session, event):
    deadname = session.name
    session.name = event
    session_manager.save_session(session.chat_id)
    logger.info(f'User "{deadname}" ("{session.username}") is now "{session.name}"')

    await bot.send_message(
        session.chat_id,
        text=(
            f"<i>Рад познакомиться, {session.name}</i>\n\n"
        ),
        parse_mode="HTML",
    )
    return