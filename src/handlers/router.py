from handlers.handlers import route_callback, route_message
from service.sessions import session_manager

class Router:
    def __init__(self):
        pass
    
    async def route_callback(self, bot, call):
        await route_callback(bot, call)
    
    async def route_message(self, bot, message):
        await route_message(bot, message)