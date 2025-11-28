import logging
from handlers.text_handler import TextHandler
from handlers.callback_handler import CallbackHandler

logger = logging.getLogger('H.router')

class Router:
    def __init__(self):
        self.text_handler = TextHandler()
        self.callback_handler = CallbackHandler()
    
    async def route_message(self, bot, message):
        await self.text_handler.handle(bot, message)
    
    async def route_callback(self, bot, call):
        await self.callback_handler.handle(bot, call)