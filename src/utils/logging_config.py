import logging

class ColoredFormatter(logging.Formatter):
    H_MODULE_COLORS = {
        'DEBUG': '\033[5;34m', 
        'INFO': '\033[5;36m', 
        'WARNING': '\033[5;35m', 
        'ERROR': '\033[5;31m'
    }

    NORMAL_MODULE_COLORS = {
        'DEBUG': '\033[2;36m', 
        'INFO': '\033[2;37m',
        'WARNING': '\033[2;33m', 
        'ERROR': '\033[2;31m'
    }
    
    RESET = '\033[0m'

    def __init__(self, show_level=True):
        super().__init__()
        self.show_level = show_level

    def format(self, record):
        is_h_module = record.name.startswith('H.')
        colors = self.H_MODULE_COLORS if is_h_module else self.NORMAL_MODULE_COLORS
        
        color = colors.get(record.levelname, self.RESET)
        if self.show_level:
            log_fmt = f"{color}[%(levelname)s] %(message)s{self.RESET}"
        else:
            log_fmt = f"{color}%(message)s{self.RESET}"

        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logging(test_mode=False):

    if test_mode:
        console_formatter = ColoredFormatter(show_level=False)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.DEBUG)

        logger = logging.getLogger()
        logger.handlers.clear() 
        logger.addHandler(console_handler)

    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(levelname)s]: %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("bot.log", "a", encoding="utf-8")
            ]
        )
        logger = logging.getLogger()

    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

    logger.setLevel(logging.DEBUG)

    return logger