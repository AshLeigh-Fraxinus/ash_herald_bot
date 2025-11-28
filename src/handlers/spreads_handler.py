from service import sessions
from .section_handler import SectionHandler
from utils import texts, keyboard, utils
from actions.spreads import daily_card, three_cards
from actions.spreads.deck import choose_deck
from actions.spreads.add_card import handle_additional_question

class SpreadsHandler(SectionHandler):
    def __init__(self):
        super().__init__()
        self.commands = {
            "cards_spread": self.handle_cards_menu,
            "🂠 обратиться к картам": self.handle_cards_menu,
            "✧ карта дня": daily_card.daily_card,
            "✦ три лика судьбы": three_cards.three_cards,
            "✥ выбрать колоду": choose_deck.choose_deck,
        }
        
        self.callbacks = {
            "cards_spread": self.handle_cards_menu,
            "daily_card": daily_card.daily_card,
            "three_cards": three_cards.three_cards,
            "additional_card": handle_additional_question,
            "choose_deck": choose_deck.choose_deck,
            'tarot_deck': choose_deck.def_deck,
            'deviant_moon_deck': choose_deck.def_deck,
            'santa_muerte_deck': choose_deck.def_deck,
            'lenorman_deck': choose_deck.def_deck,
            'persona3_deck': choose_deck.def_deck,
        }
    
    async def handle_cards_menu(self, bot, update, session):
        chat_id = await utils.get_chat_id(update)
        sessions.session_manager.reset_session(chat_id)
        await bot.send_message(
            chat_id, texts.CARDS_TEXT,
            parse_mode="HTML",
            reply_markup=keyboard.get_cards_keyboard()
        )