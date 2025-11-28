import datetime, json, logging
from utils import utils
from service.database import db_manager

logger = logging.getLogger('H.sessions')

class Session:
    def __init__(self, chat_id: str, user_data: dict):
        self.chat_id = chat_id
        self._load_from_data(user_data)

    def _load_from_data(self, data: dict):

        self._name = data.get('name', self.chat_id)
        self._state = data.get('state', 'main')
        self._deck = data.get('deck', 'tarot')
        self._city = data.get('city', '')
        self._is_waiting_for_question = bool(data.get('is_waiting_for_question', 0))
        
        self.data = self._parse_json_field(data.get('data', '{}'))
        self.messages = self._parse_json_field(data.get('messages', '[]'))

        self.created_at = self._parse_date(data.get('created_at'))
        self.last_activity = self._parse_date(data.get('last_activity'))
        self.last_daily_card_date = self._parse_date(data.get('last_daily_card_date'))

    def _parse_json_field(self, field):
        if isinstance(field, str):
            try:
                return json.loads(field)
            except (json.JSONDecodeError, TypeError):
                return {} if 'data' in str(field) else []
        return field

    def _parse_date(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            return None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self._save_to_db()

    @property
    def deck(self):
        return self._deck

    @deck.setter
    def deck(self, value):
        self._deck = value
        self._save_to_db()
    
    @property
    def city(self):
        return self._city

    @city.setter
    def city(self, value):
        self._city = value
        self._save_to_db()

    @property
    def is_waiting_for_question(self):
        return self._is_waiting_for_question

    @is_waiting_for_question.setter
    def is_waiting_for_question(self, value):
        self._is_waiting_for_question = value
        self._save_to_db()

    def can_draw_daily_card(self) -> bool:
        if self.last_daily_card_date is None:
            return True

        today = datetime.date.today()
        last_date = self.last_daily_card_date.date() if isinstance(self.last_daily_card_date, datetime.datetime) else self.last_daily_card_date

        can_draw = last_date < today
        logger.debug(f"{self.name} has already requested daily card today") if not can_draw else logger.debug(f"{self.name} can request daily card")

        return can_draw

    def mark_daily_card_drawn(self):
        self.last_daily_card_date = datetime.datetime.now()
        self.update_activity()
        self._save_to_db()
        logger.debug(f"User: {self.name}, daily_card marked for today")

    def update_activity(self):
        self.last_activity = datetime.datetime.now()
        self._save_to_db()

    def update_session_data(self, data=None, messages=None):
        if data is not None:
            self.data = data
        if messages is not None:
            self.messages = messages
        self._save_to_db()

    def reset(self):
        old_state = self.state
        self.state = 'main'
        self.data = {}
        self.is_waiting_for_question = False
        self.messages = []
        self.update_activity()
        self._save_to_db()

        logger.debug(f"✥ Путь перезапущен для: {self.name} (из состояния: {old_state})")

    def get_session_info(self) -> dict:
        return {
            'name': self.name,
            'state': self.state,
            'deck': self.deck,
            'has_daily_card': not self.can_draw_daily_card(),
            'created': self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "N/A",
            'last_activity': self.last_activity.strftime("%Y-%m-%d %H:%M") if self.last_activity else "N/A"
        }

    def _save_to_db(self):
        db_manager.update_user(
            self.chat_id,
            state=self.state,
            deck=self.deck,
            city=self.city,
            last_daily_card_date=self.last_daily_card_date.isoformat() if self.last_daily_card_date else None,
            last_activity=self.last_activity.isoformat() if self.last_activity else None
        )
        
        db_manager.update_session_data(
            self.chat_id,
            data=self.data,
            messages=self.messages,
            is_waiting_for_question=self.is_waiting_for_question
        )

class SessionManager:
    def __init__(self):
        self.db_manager = db_manager

    def get_session(self, chat_id: str, name: str = None) -> Session:
        user_data = self.db_manager.get_user(chat_id)
        
        if not user_data:
            username, first_name, last_name = "", "", ""
            if name and isinstance(name, tuple):
                username, first_name, last_name = name
            elif name:
                first_name = name
                
            display_name = utils.get_clean_name(username, first_name, last_name) or f"user_{chat_id}"
            user_data = self.db_manager.create_user(
                chat_id, 
                name=display_name,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
        else:
            self.db_manager.update_user(chat_id, last_activity=datetime.datetime.now().isoformat())
            user_data = self.db_manager.get_user(chat_id) 
            
        return Session(chat_id, user_data)

    def reset_session(self, chat_id: str):
        self.db_manager.reset_session(chat_id)

    def get_name(self, chat_id: str, name_tuple: tuple) -> str:
        username, first_name, last_name = name_tuple
        user_data = self.db_manager.get_user(chat_id)
        
        if user_data and user_data.get('name'):
            return user_data['name']
        
        return utils.get_clean_name(username, first_name, last_name) or f"user_{chat_id}"

    def cleanup_inactive_sessions(self, days: int = 7):
        self.db_manager.cleanup_inactive_sessions(days)

    def get_session_stats(self) -> dict:
        return self.db_manager.get_session_stats()

    def get_all_sessions(self) -> list:
        users_data = self.db_manager.get_all_users()
        return [Session(user_data['chat_id'], user_data) for user_data in users_data]

session_manager = SessionManager()