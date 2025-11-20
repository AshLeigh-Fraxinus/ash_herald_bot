import logging
from telebot import types

from ash_herald import sessions, texts
from ash_herald.utils import keyboard, utils
from ash_herald.actions.moon import moon_day
from ash_herald.handlers.spreads_handler import SpreadHandler

logger = logging.getLogger('MAIN_HANDLER')

class MessageHandler:
    def __init__(self):
        self.spread_handler = SpreadHandler()
    
    async def handle_all_messages(self, bot, message):
        chat_id = await utils.get_chat_id(message)
        name_tuple = utils.get_username_and_names(message)
        name = sessions.session_manager.get_name(chat_id, name_tuple)
        session = sessions.session_manager.get_session(chat_id, name)
        
        if await self.spread_handler.handle_waiting_state(bot, message, session):
            return
        
        logger.debug(f"User: {session.name}, text: {message.text}")
        
        if await self._handle_message(bot, message, session):
            return
        
        await self._handle_unknown_message(bot, message, session)
    
    async def _handle_message(self, bot, message, session) -> bool:
        text = message.text.strip().lower()
        
        handlers = {
            "start": self.handle_start,
            "⛧ к истокам": self._handle_thanks,
            "/thanks": self._handle_thanks,
            "thanks": self._handle_thanks,
            "🂠 обратиться к картам": self._handle_cards_spread,
            "/cards_spread": self._handle_cards_spread,
            "cards_spread": self._handle_cards_spread,
            "☽ обратиться к луне": self._handle_moon_day,
            "/moon_day": self._handle_moon_day,
            "moon_day": self._handle_moon_day,
        }
        
        for key, handler in handlers.items():
            if key in text:
                await handler(bot, message, session)
                return True
        return False
    
    async def handle_start(self, bot, message, session=None):
        chat_id = await utils.get_chat_id(message)
        if session is None:
            name_tuple = utils.get_username_and_names(message)
            name = sessions.session_manager.get_name(chat_id, name_tuple)
            session = sessions.session_manager.get_session(chat_id, name)
        
        logger.debug(f"User: {session.name}, action: /start")
        sessions.session_manager.reset_session(chat_id)
        await bot.send_message(
            chat_id, texts.START_TEXT, 
            parse_mode="HTML", 
            reply_markup=keyboard.get_main_keyboard()
        )
    
    async def _handle_thanks(self, bot, message, session):
        await self.spread_handler.handle_thanks(bot, message, session)
    
    async def _handle_cards_spread(self, bot, message, session):
        await self.spread_handler.handle_spread(bot, message)
    
    async def _handle_moon_day(self, bot, message, session):
        await moon_day.moon_day(bot, message, session)
    
    async def _handle_unknown_message(self, bot, message, session):
        chat_id = await utils.get_chat_id(message)
        text = message.text
        
        if session.is_waiting_for_question:
            logger.debug(f"User: {session.name}, waiting answer: {text}")
            session.is_waiting_for_question = False
            session.data['user_answer'] = text
            await bot.send_message(
                chat_id, texts.START_TEXT, 
                parse_mode="HTML", 
                reply_markup=keyboard.get_main_keyboard()
            )
        else:
            logger.warning(f"User: {session.name}, unknown command: {text}")
            await bot.send_message(chat_id, texts.UNKNOWN_COMMAND_TEXT, parse_mode="HTML")

class CallbackHandler:
    def __init__(self):
        self.spread_handler = SpreadHandler()
    
    async def handle_callbacks(self, bot, call):
        chat_id = await utils.get_chat_id(call)
        name_tuple = utils.get_username_and_names(call)
        name = sessions.session_manager.get_name(chat_id, name_tuple)
        session = sessions.session_manager.get_session(chat_id, name)
        
        logger.debug(f"User: {session.name}, callback: {call.data}")
        
        try:
            await self._clear_message_markup(bot, call, chat_id)
        except Exception as e:
            logger.debug(f"Non-critical error clearing markup: {e}")
        
        try:
            if await self.spread_handler.handle_callback(bot, call, session):
                return
            
            await self._handle_callback(bot, call, session)
        except Exception as e:
            logger.error(f"User: {session.name}, error: {e}")
            if "message is not modified" not in str(e):
                await bot.send_message(chat_id, texts.ERROR_TEXT, parse_mode="HTML")
    
    async def _clear_message_markup(self, bot, call, chat_id):
        try:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=None
            )
        except Exception as e:
            if "message is not modified" in str(e):
                logger.debug(f"Message not modified (expected): {e}")
            else:
                logger.warning(f"Could not edit message markup: {e}")
    
    async def _handle_callback(self, bot, call, session):
        chat_id = await utils.get_chat_id(call)
        
        callback_handlers = {
            "start": self._handle_start_callback,
            "/start": self._handle_start_callback,
            "moon_day": self._handle_moon_day_callback,
            "cards_spread": self._handle_cards_spread_callback,
        }
        
        handler = callback_handlers.get(call.data)
        if handler:
            await handler(bot, call, session)
        else:
            logger.debug(f"User: {session.name}, unknown callback: {call.data}")
            await bot.send_message(chat_id, texts.UNKNOWN_COMMAND_TEXT, parse_mode="HTML")
    
    async def _handle_start_callback(self, bot, call, session):
        logger.debug(f"User: {session.name}, callback: start")
        await MessageHandler().handle_start(bot, call, session)
    
    async def _handle_moon_day_callback(self, bot, call, session):
        logger.debug(f"User: {session.name}, callback: moon_day")
        from ash_herald.actions.moon import moon_day
        await moon_day.moon_day(bot, call, session)
    
    async def _handle_cards_spread_callback(self, bot, call, session):
        logger.debug(f"User: {session.name}, callback: cards_spread")
        await self.spread_handler.handle_spread(bot, call)