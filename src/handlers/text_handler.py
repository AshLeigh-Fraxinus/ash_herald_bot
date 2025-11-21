from service import sessions
from utils import utils, texts, keyboard
from actions.moon import moon_day
from actions.spreads import daily_card, three_cards
from actions.spreads.deck import choose_deck

class TextHandler:
    def __init__(self):
        self.commands = self._setup_commands()
        self.text_handlers = self._setup_text_handlers()
    
    def _setup_commands(self):
        return {
            "start": self._handle_start,
            "/start": self._handle_start,
            "thanks": self._handle_thanks,
            "⛧ к истокам": self._handle_thanks,
            "cards_spread": self._handle_cards_spread,
            "🂠 обратиться к картам": self._handle_cards_spread,
            "moon_day": self._handle_moon_day,
            "☽ обратиться к луне": self._handle_moon_day,
        }
    
    def _setup_text_handlers(self):
        return {
            "✧ карта дня": daily_card.daily_card,
            "✦ три лика судьбы": three_cards.three_cards,
            "✥ выбрать колоду": choose_deck.choose_deck,
        }
    
    async def handle(self, bot, message):
        session = await self._get_session(bot, message)
        text = message.text.strip().lower()
        
        if await self._handle_waiting_state(bot, message, session):
            return
        
        for cmd, handler in self.commands.items():
            if cmd in text:
                await handler(bot, message, session)
                return
        
        for key, handler in self.text_handlers.items():
            if key.lower() in text:
                await handler(bot, message, session)
                return

        await self._handle_unknown(bot, message, session)
    
    async def _get_session(self, bot, message):
        chat_id = await utils.get_chat_id(message)
        name_tuple = utils.get_username_and_names(message)
        name = sessions.session_manager.get_name(chat_id, name_tuple)
        return sessions.session_manager.get_session(chat_id, name)
    
    async def _handle_waiting_state(self, bot, message, session):
        if session.state == "waiting_for_three_cards_question":
            from actions.spreads.three_cards import handle_three_cards_question
            await handle_three_cards_question(bot, message, session)
            return True
        elif session.state == "waiting_for_additional_question":
            from actions.spreads.add_card import handle_additional_question
            await handle_additional_question(bot, message, session)
            return True
        elif session.state == "choosing_deck":
            from actions.spreads.deck import def_deck
            await def_deck(bot, message, session)
            return True
        return False
    
    async def _handle_start(self, bot, message, session):
        chat_id = await utils.get_chat_id(message)
        sessions.session_manager.reset_session(chat_id)
        await bot.send_message(
            chat_id, texts.START_TEXT,
            parse_mode="HTML",
            reply_markup=keyboard.get_main_keyboard()
        )
    
    async def _handle_thanks(self, bot, message, session):
        chat_id = await utils.get_chat_id(message)
        sessions.session_manager.reset_session(chat_id)
        await bot.send_message(
            chat_id, texts.THANKS_TEXT,
            parse_mode="HTML",
            reply_markup=keyboard.get_main_keyboard()
        )
    
    async def _handle_cards_spread(self, bot, message, session):
        chat_id = await utils.get_chat_id(message)
        sessions.session_manager.reset_session(chat_id)
        await bot.send_message(
            chat_id, texts.CARDS_TEXT,
            parse_mode="HTML",
            reply_markup=keyboard.get_cards_keyboard()
        )
    
    async def _handle_moon_day(self, bot, message, session):
        await moon_day.moon_day(bot, message, session)
    
    async def _handle_unknown(self, bot, message, session):
        chat_id = await utils.get_chat_id(message)
        if session.is_waiting_for_question:
            session.is_waiting_for_question = False
            session.data['user_answer'] = message.text
            await self._handle_start(bot, message, session)
        else:
            await bot.send_message(chat_id, texts.UNKNOWN_COMMAND_TEXT, parse_mode="HTML")