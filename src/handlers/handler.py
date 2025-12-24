import logging
from service.sessions import session_manager

from actions.moon.day import moon_day
from handlers.handle_cards import handle_cards, handle_unknown_command
from handlers.handle_weather import handle_weather
from handlers.handle_change import handle_settings
from handlers.handle_admin import handle_admin
from handlers.handle_common import handle_common

logger = logging.getLogger('H.handler')

HANDLERS = {
    '/start': lambda bot, session, event: handle_common(bot, session, event),
    'thanks': lambda bot, session, event: handle_common(bot, session, event),
    'support': lambda bot, session, event: handle_common(bot, session, event),
    
    'cards_': lambda bot, session, event: handle_cards(bot, session, event),
    'change_': lambda bot, session, event: handle_settings(bot, session, event),
    'moon_': lambda bot, session, event: moon_day(bot, session),
    'weather_': lambda bot, session, event: handle_weather(bot, session, event),
    '/get_users_from_database': lambda bot, session, event: handle_admin(bot, session, event)
}

class Handler:
    def __init__(self):
        pass
    
    async def handle_message(self, bot, message):
        user_info = message.from_user
        chat_id = user_info.id
        session = session_manager.get_session(chat_id, user_info)
        event = message.text
        await self._process_event(bot, session, event)

    async def handle_callback(self, bot, call):
        user_info = call.from_user
        chat_id = user_info.id
        session = session_manager.get_session(chat_id, user_info)
        event = call.data
        await self._process_event(bot, session, event)

    async def _process_event(self, bot, session, event):
        try:
            session.update_activity()
            logger.debug(f'"{session.username}" wrote "{event}" in "{session.state}"')
            
            for prefix, handler in HANDLERS.items():
                if session.state.startswith(prefix) or event.startswith(prefix):
                    await handler(bot, session, event)
                    return
            
            logger.warning(f'Error handling message "{event}" for "{session.username}" in "{session.state}": {e}')
            await handle_unknown_command(bot, session)
                
        except Exception as e:
            logger.error(f'Error handling message "{event}" for "{session.username}" in "{session.state}": {e}')
            await handle_unknown_command(bot, session)
