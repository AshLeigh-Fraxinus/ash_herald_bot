import os, time, asyncio, logging

from ash_herald.handlers.main_handler import button_callback_handler, handle_all_messages, handle_start
from dotenv import load_dotenv
from ash_herald.database import db_manager
from telebot.async_telebot import AsyncTeleBot

shutdown_requested = False

class TelegramBot:
    def __init__(self):
        self.logger = logging.getLogger('BOT')
        self.bot = self.configure_bot()
        self.setup_handlers()
    
    def configure_bot(self):
        load_dotenv()
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        if not BOT_TOKEN:
            self.logger.error("Токен бота не найден в переменных окружения")
            raise ValueError("Токен бота не найден в переменных окружения")
        return AsyncTeleBot(BOT_TOKEN)
    
    def setup_handlers(self):
        
        #------------------
        # Обработка команды start
        #------------------
        @self.bot.message_handler(commands=['start'])
        async def start(message):
            await handle_start(self.bot, message)

        #-------------------
        # Получение текста
        #-------------------
        @self.bot.message_handler(func=lambda message: True)
        async def handle_messages(message):
            await handle_all_messages(self.bot, message)

        #------------------
        # Обработка кнопок
        #------------------
        @self.bot.callback_query_handler(func=lambda call: True)
        async def handle_callbacks(call):
            await button_callback_handler(self.bot, call)

    def signal_handler(self, signum, frame):
        global shutdown_requested
        self.logger.info("Herald shutting down gracefully...")
        shutdown_requested = True

        db_manager.cleanup_inactive_sessions(days=7)
        
        import threading
        def force_exit():
            time.sleep(2)
            os._exit(0)
        threading.Thread(target=force_exit).start()
    
    async def run_async(self):
        global shutdown_requested

        db_manager.cleanup_inactive_sessions(days=7)
        
        self.logger.info("Herald is active ...")
        
        import signal
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        while not shutdown_requested:
            try:
                await self.bot.polling(non_stop=True, timeout=30)
            except asyncio.CancelledError:
                self.logger.info("Bot polling cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in async run: {e}")
                await asyncio.sleep(5)

    def run(self):
        asyncio.run(self.run_async())