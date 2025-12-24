import logging, datetime, json, sqlite3
from typing import Optional, Dict, Any, List

logger = logging.getLogger('H.database')

class DatabaseManager:
    def __init__(self, db_path: str = "database/sessions.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    chat_id TEXT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    name TEXT,
                    state TEXT DEFAULT 'main',
                    deck TEXT DEFAULT 'tarot',
                    city TEXT DEFAULT '',
                    last_daily_card_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_activity TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_data (
                    chat_id TEXT PRIMARY KEY,
                    data TEXT,
                    messages TEXT,
                    is_waiting_for_question INTEGER DEFAULT 0,
                    FOREIGN KEY (chat_id) REFERENCES users (chat_id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
        logger.debug("Database initialized successfully")

    def get_user(self, chat_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.*, sd.data, sd.messages, sd.is_waiting_for_question
                FROM users u
                LEFT JOIN session_data sd ON u.chat_id = sd.chat_id
                WHERE u.chat_id = ?
            ''', (chat_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def create_user(self, chat_id: str, name: str = None, username: str = None, first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        now = datetime.datetime.now().isoformat()
        display_name = name or first_name or f"user_{chat_id}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (chat_id, username, first_name, last_name, name, created_at, last_activity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (chat_id, username, first_name, last_name, display_name, now, now))
            
            cursor.execute('''
                INSERT OR IGNORE INTO session_data (chat_id, data, messages)
                VALUES (?, '{}', '[]')
            ''', (chat_id,))
            
            conn.commit()
        return self.get_user(chat_id)

    def update_user(self, chat_id: str, **kwargs):
        if not kwargs:
            return
            
        allowed_fields = {
            'state', 'deck', 'last_daily_card_date', 'username', 'first_name', 'last_name', 'name',
            'last_activity', 'city'
        }
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return
            
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [chat_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE users SET {set_clause} WHERE chat_id = ?', values)
            conn.commit()

    def update_session_data(self, chat_id: str, data: Dict = None, messages: List = None, is_waiting_for_question: bool = None):
        updates = []
        values = []
        
        if data is not None:
            updates.append("data = ?")
            values.append(json.dumps(data, ensure_ascii=False))
        
        if messages is not None:
            updates.append("messages = ?")
            values.append(json.dumps(messages, ensure_ascii=False))
            
        if is_waiting_for_question is not None:
            updates.append("is_waiting_for_question = ?")
            values.append(1 if is_waiting_for_question else 0)
        
        if not updates:
            return
            
        values.append(chat_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE session_data 
                SET {", ".join(updates)} 
                WHERE chat_id = ?
            ''', values)
            conn.commit()

    def reset_session(self, chat_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT state, name FROM users WHERE chat_id = ?', (chat_id,))
            result = cursor.fetchone()
            name = result[1] if result else 'unknown'

            cursor.execute('''
                UPDATE users 
                SET state = 'main', last_activity = ?
                WHERE chat_id = ?
            ''', (datetime.datetime.now().isoformat(), chat_id))
            
            cursor.execute('''
                UPDATE session_data 
                SET data = '{}', messages = '[]', is_waiting_for_question = 0
                WHERE chat_id = ?
            ''', (chat_id,))
            
            conn.commit()

    def get_all_users(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.*, sd.data, sd.messages, sd.is_waiting_for_question
                FROM users u
                LEFT JOIN session_data sd ON u.chat_id = sd.chat_id
            ''')
            
            return [dict(row) for row in cursor.fetchall()]

    def cleanup_inactive_sessions(self, days: int = 14):
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name FROM users 
                WHERE last_activity < ?
            ''', (cutoff_date,))
            
            inactive_users = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('DELETE FROM users WHERE last_activity < ?', (cutoff_date,))
            deleted_count = cursor.rowcount
            
            conn.commit()
        logger.debug(f"Reset {deleted_count} inactive sessions: {', '.join(inactive_users)}") if inactive_users else logger.debug("No inactive sessions to clean up")

db_manager = DatabaseManager()
