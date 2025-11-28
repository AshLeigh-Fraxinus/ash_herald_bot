from service import sessions
import utils
from .section_handler import SectionHandler
from utils import texts, keyboard

class MainHandler(SectionHandler):
    def __init__(self):
        super().__init__()
        self.commands = {
            "start": self.handle_start,
            "/start": self.handle_start,
            "thanks": self.handle_thanks,
            "⛧ к истокам": self.handle_thanks,
        }
        
        self.callbacks = {
            "start": self.handle_start,
            "thanks": self.handle_thanks,
        }
    
    async def handle_start(self, bot, update, session):
        chat_id = await utils.get_chat_id(update)
        sessions.session_manager.reset_session(chat_id)
        await bot.send_message(
            chat_id, texts.START_TEXT,
            parse_mode="HTML",
            reply_markup=keyboard.get_main_keyboard()
        )
    
    async def handle_thanks(self, bot, update, session):
        chat_id = await utils.get_chat_id(update)
        sessions.session_manager.reset_session(chat_id)
        await bot.send_message(
            chat_id, texts.THANKS_TEXT,
            parse_mode="HTML", 
            reply_markup=keyboard.get_main_keyboard()
        )