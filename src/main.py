import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

sys.dont_write_bytecode=True

import logging
import bot as bot

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] [module: %(name)s]: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("bot.log", "a", encoding="utf-8")
        ]
    )

    bot_instance = bot.TelegramBot()
    bot_instance.run()

if __name__ == "__main__":
    main()