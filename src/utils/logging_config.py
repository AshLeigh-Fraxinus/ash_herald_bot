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

    def format(self, record):
        is_h_module = record.name.startswith('H.')
        colors = self.H_MODULE_COLORS if is_h_module else self.NORMAL_MODULE_COLORS
        
        color = colors.get(record.levelname, self.RESET)
        log_fmt = f"{color}%(message)s{self.RESET}"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] [module: %(name)s]: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("bot.log", "a", encoding="utf-8")
        ]
    )

    console_handler = logging.getLogger().handlers[0]
    console_handler.setFormatter(ColoredFormatter())
    
    return logging.getLogger()