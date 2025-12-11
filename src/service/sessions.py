import datetime, logging, threading, time
from typing import Dict, Any, Optional, List
from utils import utils
from service.database import db_manager

logger = logging.getLogger('H.sessions')

class Session:
    def __init__(self, chat_id: str, user_data: Dict[str, Any]):
        self.chat_id = chat_id

        self.name = user_data.get('name', f"user_{chat_id}")
        self.username = user_data.get('username', '')
        self.first_name = user_data.get('first_name', '')
        self.last_name = user_data.get('last_name', '')
        self.deck = user_data.get('deck', 'tarot')
        self.city = user_data.get('city', '')

        self.state: str = 'main' 
        self.temp_data: Dict[str, Any] = {}
        self.messages: List[Dict] = [] 

        self.created_at = self._parse_date(user_data.get('created_at'))
        self.last_daily_card_date = self._parse_date(user_data.get('last_daily_card_date'))
        self.session_start = datetime.datetime.now()
        self.last_activity = datetime.datetime.now()

        self._dirty = False  

    def _parse_date(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            return None

    def update_activity(self):
        self.last_activity = datetime.datetime.now()
        self._dirty = True

    def is_expired(self, ttl_hours: int = 1) -> bool:
        expired = datetime.datetime.now() - self.last_activity > datetime.timedelta(hours=ttl_hours)
        if expired:
            logger.debug(f"Session for {self.name} expired (inactive for {ttl_hours}h)")
        return expired

    def can_draw_daily_card(self) -> bool:
        if self.last_daily_card_date is None:
            return True
        
        last_date = self.last_daily_card_date.date()
        today = datetime.date.today()
        can_draw = last_date < today
        
        logger.debug(f'"{self.name}" {"can" if can_draw else "cannot"} draw daily card')
        return can_draw

    def mark_daily_card_drawn(self):
        self.last_daily_card_date = datetime.datetime.now()
        self._dirty = True
        logger.debug(f'"{self.name}" received daily card')

    def update_temp_data(self, key: str, value: Any):
        self.temp_data[key] = value

    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat()
        })

        if len(self.messages) > 10:
            self.messages = self.messages[-10:]

    def clear_context(self):
        self.messages = []

    def reset_state(self):
        self.state = 'main'
        self.temp_data = {}
        self.clear_context()
        self.update_activity()

    def get_info(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'state': self.state,
            'deck': self.deck,
            'city': self.city,
            'has_daily_card': not self.can_draw_daily_card(),
            'session_age': str(datetime.datetime.now() - self.session_start),
            'inactivity': str(datetime.datetime.now() - self.last_activity),
            'message_count': len(self.messages),
            'temp_data_keys': list(self.temp_data.keys())
        }
    
    def is_waiting_for_input(self) -> bool:
        waiting_states = ['waiting', 'input', 'question', 'answer', 'confirm']
        return any(wait_word in self.state.lower() for wait_word in waiting_states)
    
    def save_to_db(self, db_manager) -> bool:
        if not self._dirty:
            return False
        
        try:
            db_manager.update_user(
                self.chat_id,
                name=self.name,
                deck=self.deck,
                city=self.city,
                last_daily_card_date=self.last_daily_card_date.isoformat() if self.last_daily_card_date else None,
                last_activity=self.last_activity.isoformat()
            )
            
            self._dirty = False
            logger.debug(f"Saved session data for {self.name} to DB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save session for {self.name}: {e}")
            return False

class SessionManager:
    def __init__(self, db_manager, cleanup_interval: int = 3600):
        self.db = db_manager
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.RLock()
        self._cleanup_interval = cleanup_interval 

        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        def cleanup_worker():
            while True:
                time.sleep(self._cleanup_interval)
                self.cleanup_expired_sessions()
        
        thread = threading.Thread(target=cleanup_worker, daemon=True)
        thread.start()
        logger.info(f"Session cleanup thread started (interval: {self._cleanup_interval}s)")

    def get_session(self, chat_id: str, user_info: tuple = None) -> Session:
        with self._lock:
            if chat_id in self._sessions:
                session = self._sessions[chat_id]
                session.update_activity()
                return session

            user_data = self.db.get_user(chat_id)
            
            if not user_data:
                if user_info:
                    username, first_name, last_name = user_info
                    clean_name = utils.get_clean_name(username, first_name, last_name)
                else:
                    username = first_name = last_name = ""
                    clean_name = f"user_{chat_id}"
                
                user_data = self.db.create_user(
                    chat_id,
                    name=clean_name,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                logger.info(f'Created new user "{clean_name}"')

            session = Session(chat_id, user_data)
            self._sessions[chat_id] = session
            
            logger.debug(f"Created new session for {session.name}")
            return session

    def save_session(self, chat_id: str):
        with self._lock:
            if chat_id in self._sessions:
                self._sessions[chat_id].save_to_db(self.db)

    def close_session(self, chat_id: str, save: bool = True):
        with self._lock:
            if chat_id in self._sessions:
                if save:
                    self._sessions[chat_id].save_to_db(self.db)
                del self._sessions[chat_id]
                logger.debug(f"Closed session for {chat_id}")

    def cleanup_expired_sessions(self, ttl_hours: int = 1):
        with self._lock:
            expired_sessions = []
            
            for chat_id, session in list(self._sessions.items()):
                if session.is_expired(ttl_hours):
                    session.save_to_db(self.db)
                    expired_sessions.append(session.name)
                    del self._sessions[chat_id]
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions: {', '.join(expired_sessions)}")
            else:
                logger.debug("No expired sessions to clean up")

    def get_active_sessions_count(self) -> int:
        with self._lock:
            return len(self._sessions)

    def get_session_info(self, chat_id: str) -> Optional[Dict]:
        with self._lock:
            if chat_id in self._sessions:
                return self._sessions[chat_id].get_info()
            return None

    def reset_user_session(self, chat_id: str):
        with self._lock:
            if chat_id in self._sessions:
                self._sessions[chat_id].reset_state()
            else:
                self.db.update_activity(chat_id)

    def cleanup_all_sessions(self, save: bool = True):
        with self._lock:
            count = len(self._sessions)
            if save:
                for session in self._sessions.values():
                    session.save_to_db(self.db)
            
            self._sessions.clear()
            logger.info(f"Cleaned up all {count} sessions")

    def get_all_sessions(self) -> List[Session]:
        with self._lock:
            return list(self._sessions.values())

session_manager = SessionManager(db_manager)