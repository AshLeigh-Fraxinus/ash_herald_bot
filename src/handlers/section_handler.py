from service import sessions
from utils import utils

class SectionHandler:
    
    def __init__(self):
        self.commands = {}
        self.callbacks = {}
    
    async def get_session(self, update):
        chat_id = await utils.get_chat_id(update)
        name_tuple = utils.get_username_and_names(update)
        name = sessions.session_manager.get_name(chat_id, name_tuple)
        return sessions.session_manager.get_session(chat_id, name)

    async def handle_text(self, bot, message, session):
        text = message.text.strip().lower()
        for cmd, handler in self.commands.items():
            if cmd in text:
                await handler(bot, message, session)
                return True
        return False
    
    async def handle_callback(self, bot, call, session):
        handler = self.callbacks.get(call.data)
        if handler:
            await handler(bot, call, session)
            return True
        return False