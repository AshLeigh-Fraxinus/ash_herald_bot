import logging
from .section_handler import SectionHandler
from actions.moon import moon_day

logger = logging.getLogger('H.moon_handler')

class MoonHandler(SectionHandler):
    def __init__(self):
        super().__init__()
        self.commands = {
            "moon_day": moon_day.moon_day,
            "☽ обратиться к луне": moon_day.moon_day,
        }
        
        self.callbacks = {
            "moon_day": moon_day.moon_day,
        }
