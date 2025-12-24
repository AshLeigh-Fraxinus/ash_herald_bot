import os, time, asyncio, logging, signal

from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv

from handlers.handler import Handler

class ApplicationState:
    def __init__(self):
        self.shutdown_requested = False

class TelegramBot:
    def __init__(self):
        self.logger = logging.getLogger('H.Bot')
        self.state = ApplicationState()
        self.bot = self.configure_bot()
        self.handler = Handler()
        self.setup_handlers()
    
    def configure_bot(self):
        load_dotenv()
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        if not BOT_TOKEN:
            self.logger.error("Токен бота не найден в переменных окружения")
            raise ValueError("Токен бота не найден в переменных окружения")
        return AsyncTeleBot(BOT_TOKEN)
    
    def setup_handlers(self):
        @self.bot.message_handler(content_types=['text'])
        async def handle_message(message):
            await self.handler.handle_message(self.bot, message)

        @self.bot.callback_query_handler(func=lambda call: True)
        async def handle_callback(call):
            await self.handler.handle_callback(self.bot, call)

    def signal_handler(self, signum, frame):
        self.logger.info("Herald shutting down gracefully...")
        self.state.shutdown_requested = True
        
        def force_exit():
            time.sleep(1)
            os._exit(0)
        
        import threading
        threading.Thread(target=force_exit).start()
    
    async def run_async(self):
        
        self.logger.info("Herald is active ...")
        
        import signal
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            await self.bot.polling(non_stop=True, timeout=60)
        except asyncio.CancelledError:
            self.logger.info("Bot polling cancelled")
        except Exception as e:
            self.logger.error(f"Error in async run: {e}")
            await asyncio.sleep(5)

    def run(self):
        asyncio.run(self.run_async())