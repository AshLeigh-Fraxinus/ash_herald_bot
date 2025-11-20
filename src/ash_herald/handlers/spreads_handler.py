import logging

from ash_herald.actions.spreads import daily_card, three_cards
from ash_herald.actions.spreads.add_card import handle_additional_question
from ash_herald.actions.spreads.deck import choose_deck
from ash_herald import sessions, texts
from ash_herald.utils import keyboard, utils

logger = logging.getLogger('SPREAD_HANDLER')

class SpreadHandler:
    def __init__(self):
        self.text_handlers = self._setup_text_handlers()
        self.callback_handlers = self._setup_callback_handlers()
    
    def _setup_text_handlers(self):
        return {
            "daily_card": self._handle_daily_card_text,
            "three_cards": self._handle_three_cards_text,
            "cards_spread": self._handle_spread_text,
            "✧ карта дня": self._handle_daily_card_text,
            "✦ три лика судьбы": self._handle_three_cards_text,
            "✥ выбрать колоду": self._handle_choose_deck_text,
        }
    
    def _setup_callback_handlers(self):
        return {
            "daily_card": self._handle_daily_card_callback,
            "three_cards": self._handle_three_cards_callback,
            "additional_card": self._handle_additional_card_callback,
            "choose_deck": self._handle_choose_deck_callback,
            'tarot_deck': self._handle_deck_selection_callback,
            'deviant_deck': self._handle_deck_selection_callback,
            'muerte_deck': self._handle_deck_selection_callback,
            'lenorman_deck': self._handle_deck_selection_callback,
            "thanks": self._handle_thanks_callback,
        }
    
    async def handle_spread(self, bot, message):
        chat_id = await utils.get_chat_id(message)
        sessions.session_manager.reset_session(chat_id)
        await bot.send_message(
            chat_id, texts.CARDS_TEXT, 
            parse_mode="HTML", 
            reply_markup=keyboard.get_cards_keyboard()
        )
    
    async def handle_thanks(self, bot, obj, session=None):
        chat_id = await utils.get_chat_id(obj)
        if session is None:
            name_tuple = utils.get_username_and_names(obj)
            name = sessions.session_manager.get_name(chat_id, name_tuple)
            session = sessions.session_manager.get_session(chat_id, name)
        
        logger.debug(f"User: {session.name}, returning to main menu")
        sessions.session_manager.reset_session(chat_id)
        await bot.send_message(
            chat_id, texts.THANKS_TEXT, 
            parse_mode="HTML", 
            reply_markup=keyboard.get_main_keyboard()
        )
    
    async def handle_message(self, bot, message, session) -> bool:
        text = message.text.strip().lower()
        
        for key, handler in self.text_handlers.items():
            if key in text:
                await handler(bot, message, session)
                return True
        return False
    
    async def handle_callback(self, bot, call, session) -> bool:
        logger.debug(f"User: {session.name}, callback: {call.data}")
        
        handler = self.callback_handlers.get(call.data)
        if handler:
            await handler(bot, call, session)
            return True
        return False
    
    async def handle_waiting_state(self, bot, message, session) -> bool:
        if session.state == "waiting_for_three_cards_question":
            await three_cards.handle_three_cards_question(bot, message, session)
            return True
        
        elif session.state == "waiting_for_additional_question":
            await handle_additional_question(bot, message, session)
            return True
        
        elif session.state == "choosing_deck" and hasattr(message, 'text'):
            await choose_deck.def_deck(bot, message, session)
            return True
        
        return False
    
    # Text handlers
    async def _handle_daily_card_text(self, bot, message, session):
        await daily_card.daily_card(bot, message, session)
    
    async def _handle_three_cards_text(self, bot, message, session):
        await three_cards.three_cards(bot, message, session)
    
    async def _handle_spread_text(self, bot, message, session):
        await self.handle_spread(bot, message)
    
    async def _handle_choose_deck_text(self, bot, message, session):
        await choose_deck.choose_deck(bot, message, session)
    
    # Callback handlers
    async def _handle_daily_card_callback(self, bot, call, session):
        await daily_card.daily_card(bot, call, session)
    
    async def _handle_three_cards_callback(self, bot, call, session):
        await three_cards.three_cards(bot, call, session)
    
    async def _handle_additional_card_callback(self, bot, call, session):
        await handle_additional_question(bot, call, session)
    
    async def _handle_choose_deck_callback(self, bot, call, session):
        await choose_deck.choose_deck(bot, call, session)
    
    async def _handle_deck_selection_callback(self, bot, call, session):
        await choose_deck.def_deck(bot, call, session)
    
    async def _handle_thanks_callback(self, bot, call, session):
        await self.handle_thanks(bot, call, session)