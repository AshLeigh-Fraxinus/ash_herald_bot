import logging, datetime, json, sqlite3, os
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from service.migrations import DatabaseMigrator

logger = logging.getLogger('H.database')

class DatabaseManager:
    def __init__(self, db_path: str = "database/sessions.db"):
        self.db_path = db_path
        self._run_migrations()
        self.init_database()

    def _run_migrations(self):
        load_dotenv()
        BOT_TOKEN = os.getenv("BOT_TOKEN")

        migrator = DatabaseMigrator(self.db_path)
        try:
            migrated = migrator.migrate_if_needed()
            if migrated:
                logger.info("Database migrations applied successfully")
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise

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
                deck TEXT DEFAULT 'tarot',
                city TEXT DEFAULT '',
                last_cards_daily_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_activity TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

        logger.debug("Database initialized successfully")

    def get_user(
            self, 
            chat_id: str
            ) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_user(
            self, 
            chat_id: str, 
            name: str = None, 
            username: str = None, 
            first_name: str = None, 
            last_name: str = None
            ) -> Dict[str, Any]:
        
        now = datetime.datetime.now().isoformat()
        display_name = name or first_name or f"user_{chat_id}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO users 
                (chat_id, username, first_name, last_name, name, created_at, last_activity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (chat_id, username, first_name, last_name, display_name, now, now))
            
            conn.commit()
        
        return self.get_user(chat_id)

    def update_user(self, chat_id: str, **kwargs):
        if not kwargs:
            return
            
        allowed_fields = {
            'username', 'first_name', 'last_name', 'name', 'last_activity', 'deck', 'city', 'last_cards_daily_date',
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

    def update_activity(self, chat_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET last_activity = ? 
                WHERE chat_id = ?
            ''', (datetime.datetime.now().isoformat(), chat_id))
            conn.commit()

    def get_all_users(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            return [dict(row) for row in cursor.fetchall()]

    def cleanup_inactive_users(self, days: int = 30):
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT name FROM users WHERE last_activity < ?', (cutoff_date,))
            inactive_users = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('DELETE FROM users WHERE last_activity < ?', (cutoff_date,))
            deleted_count = cursor.rowcount
            
            conn.commit()
        
        if inactive_users:
            logger.info(f'Removed {deleted_count} inactive users: {", ".join(inactive_users)}')
        else:
            logger.debug("No inactive users to clean up")

db_manager = DatabaseManager()
