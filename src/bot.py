import os, time, asyncio, logging, signal

from telebot.async_telebot import AsyncTeleBot
from service.database import db_manager
from dotenv import load_dotenv

# Импортируем Router из handlers
from handlers.router import Router

class ApplicationState:
    def __init__(self):
        self.shutdown_requested = False

class TelegramBot:
    def __init__(self):
        self.logger = logging.getLogger('H.Bot')
        self.state = ApplicationState()
        self.bot = self.configure_bot()
        self.router = Router()  # Создаем экземпляр Router
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
        async def handle_text_messages(message):
            await self.router.route_message(self.bot, message)

        @self.bot.callback_query_handler(func=lambda call: True)
        async def handle_callback(call):
            await self.router.route_callback(self.bot, call)

    def signal_handler(self, signum, frame):
        self.logger.info("Herald shutting down gracefully...")
        self.state.shutdown_requested = True
        db_manager.cleanup_inactive_sessions(days=7)
        
        def force_exit():
            time.sleep(2)
            os._exit(0)
        
        import threading
        threading.Thread(target=force_exit).start()
    
    async def _run_polling(self):
        while not self.state.shutdown_requested:
            try:
                await self.bot.polling(non_stop=True, timeout=30)
            except asyncio.CancelledError:
                self.logger.info("Bot polling cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in async run: {e}")
                await asyncio.sleep(5)
    
    async def run_async(self):
        db_manager.cleanup_inactive_sessions(days=7)
        self.logger.info("Herald is active ...")
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        await self._run_polling()
    
    def run(self):
        asyncio.run(self.run_async())

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()