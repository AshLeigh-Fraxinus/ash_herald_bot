import logging
from service import sessions
from utils import keyboard, utils, texts
from actions.moon import moon_day
from actions.spreads import daily_card, three_cards
from actions.spreads.deck import choose_deck
from actions.weather.weather import change_city
from actions.spreads.add_card import handle_additional_question

logger = logging.getLogger('H.callback_handler')

class CallbackHandler:
    def __init__(self):
        self.handlers = self._setup_handlers()
    
    def _setup_handlers(self):
        return {
            "start": self._handle_start,
            "moon_day": moon_day.moon_day,
            "cards_spread": self._handle_cards_spread,
            "daily_card": daily_card.daily_card,
            "three_cards": three_cards.three_cards,
            "additional_card": handle_additional_question,
            "choose_deck": choose_deck.choose_deck,
            "thanks": self._handle_thanks,
            'tarot_deck': choose_deck.def_deck,
            'deviant_moon_deck': choose_deck.def_deck,
            'santa_muerte_deck': choose_deck.def_deck,
            'lenorman_deck': choose_deck.def_deck,
            'persona3_deck': choose_deck.def_deck,
            "change_city": self._handle_change_city,
            "weather_today": self._handle_weather_today,
        }
    
    async def handle(self, bot, call):
        session = await self._get_session(bot, call)
        logger.debug(f"User: {session.name}, callback: {call.data}")
        
        try:
            await self._clear_message_markup(bot, call)
            handler = self.handlers.get(call.data)
            
            if handler:
                await handler(bot, call, session)
            else:
                await self._handle_unknown(bot, call, session)
                
        except Exception as e:
            await self._handle_error(bot, call, session, e)
    
    async def _get_session(self, bot, call):
        chat_id = await utils.get_chat_id(call)
        name_tuple = utils.get_username_and_names(call)
        name = sessions.session_manager.get_name(chat_id, name_tuple)
        return sessions.session_manager.get_session(chat_id, name)
    
    async def _clear_message_markup(self, bot, call):
        chat_id = await utils.get_chat_id(call)
        try:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=None
            )
        except Exception as e:
            if "message is not modified" not in str(e):
                logger.warning(f"Could not edit message markup: {e}")
    
    async def _handle_start(self, bot, call, session):
        from handlers.text_handler import TextHandler
        await TextHandler()._handle_start(bot, call, session)
    
    async def _handle_thanks(self, bot, call, session):
        chat_id = await utils.get_chat_id(call)
        sessions.session_manager.reset_session(chat_id)
        await bot.send_message(
            chat_id, texts.THANKS_TEXT,
            parse_mode="HTML",
            reply_markup=keyboard.get_main_keyboard()
        )
    
    async def _handle_cards_spread(self, bot, call, session):
        chat_id = await utils.get_chat_id(call)
        sessions.session_manager.reset_session(chat_id)
        await bot.send_message(
            chat_id, texts.CARDS_TEXT,
            parse_mode="HTML",
            reply_markup=keyboard.get_cards_keyboard()
        )

    async def _handle_change_city(self, bot, call, session):
        from actions.weather.weather import change_city
        await change_city(bot, call, session)
    
    async def _handle_weather_today(self, bot, call, session):
        from actions.weather.weather import weather_today
        await weather_today(bot, call, session)

    async def _handle_unknown(self, bot, call, session):
        chat_id = await utils.get_chat_id(call)
        await bot.send_message(chat_id, texts.UNKNOWN_COMMAND_TEXT, parse_mode="HTML")
    
    async def _handle_error(self, bot, call, session, error):
        logger.error(f"User: {session.name}, error: {error}")
        if "message is not modified" not in str(error):
            chat_id = await utils.get_chat_id(call)
            await bot.send_message(chat_id, texts.ERROR_TEXT, parse_mode="HTML")