import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.dont_write_bytecode = True

import bot as bot
from utils.logging_config import setup_logging

def main():
    logger = setup_logging()
    bot_instance = bot.TelegramBot()
    bot_instance.run()

if __name__ == "__main__":
    main()