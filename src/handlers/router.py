import logging

from service import sessions
from .main_handler import MainHandler
from .spreads_handler import SpreadsHandler
from .moon_handler import MoonHandler
from .weather_handler import WeatherHandler
from utils import utils, get_chat_id, get_username_and_names, texts, keyboard

logger = logging.getLogger('H.router')

class Router:
    def __init__(self):
        self.handlers = {
            'main': MainHandler(),
            'cards': SpreadsHandler(), 
            'moon': MoonHandler(),
            'weather': WeatherHandler(),
        }
        
        self.state_handlers = {
            "waiting_for_three_cards_question": 'cards',
            "waiting_for_additional_question": 'cards', 
            "choosing_deck": 'cards',
            "waiting_for_city": 'weather'
        }
    
    async def route_message(self, bot, message):
        session = await self._get_session(message)
        logger.debug(f"Session state: {session.state}, active_section: {session.data.get('active_section')}")

        if await self._handle_waiting_state(bot, message, session):
            return

        active_section = session.data.get('active_section', 'main')
        if await self.handlers[active_section].handle_text(bot, message, session):
            return

        for section_name, handler in self.handlers.items():
            if section_name != active_section:
                if await handler.handle_text(bot, message, session):
                    session.data['active_section'] = section_name
                    return

        await self._handle_unknown(bot, message, session)
    
    async def route_callback(self, bot, call):
        session = await self._get_session(call)
        for section_name, handler in self.handlers.items():
            if await handler.handle_callback(bot, call, session):
                session.data['active_section'] = section_name
                return
        
        await self._handle_unknown_callback(bot, call, session)
    
    async def _get_session(self, update):
        chat_id = await utils.get_chat_id(update)
        name_tuple = utils.get_username_and_names(update)
        name = sessions.session_manager.get_name(chat_id, name_tuple)
        return sessions.session_manager.get_session(chat_id, name)
    
    async def _handle_waiting_state(self, bot, message, session):
        if session.state in self.state_handlers:
            section = self.state_handlers[session.state]
            result = await self.handlers[section].handle_text(bot, message, session)
            if result:
                session.data['active_section'] = section
                await session.save()
            return result
        return False
    
    async def _handle_unknown(self, bot, message, session):
        chat_id = await utils.get_chat_id(message)
        if session.is_waiting_for_question:
            session.is_waiting_for_question = False
            session.data['user_answer'] = message.text
            await self.handlers['main'].handle_start(bot, message, session)
        else:
            await bot.send_message(chat_id, texts.UNKNOWN_COMMAND_TEXT, parse_mode="HTML")
    
    async def _handle_unknown_callback(self, bot, call, session):
        chat_id = await utils.get_chat_id(call)
        await bot.send_message(
            chat_id, 
            texts.UNKNOWN_COMMAND_TEXT,
            parse_mode="HTML",
            reply_markup=keyboard.get_main_keyboard()
        )