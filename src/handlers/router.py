import logging
from handlers.handlers import route_callback, route_message

logger = logging.getLogger('H.router')

class Router:
    def __init__(self):
        pass
    
    async def route_callback(self, bot, call):
        """Маршрутизация callback-запросов"""
        await route_callback(bot, call)
    
    async def route_message(self, bot, message):
        """Маршрутизация текстовых сообщений"""
        await route_message(bot, message)