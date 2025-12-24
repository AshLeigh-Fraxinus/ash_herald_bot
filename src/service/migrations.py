import sqlite3, logging, os, requests, time
from typing import Optional

logger = logging.getLogger('H.migrations')

class DatabaseMigrator:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.version_table = "__db_version"
        self.current_version = 3  
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        
    def migrate_if_needed(self) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.version_table} (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            ''')

            cursor.execute(f'SELECT MAX(version) as max_version FROM {self.version_table}')
            result = cursor.fetchone()
            db_version = result['max_version'] if result and result['max_version'] else 0
            
            logger.info(f"Current DB version: {db_version}, target version: {self.current_version}")
            
            if db_version >= self.current_version:
                logger.info("Database is up to date, no migration needed")
                return False

            for version in range(db_version + 1, self.current_version + 1):
                migration_method = getattr(self, f'migrate_to_v{version}', None)
                if migration_method:
                    logger.info(f"Applying migration to version {version}")
                    try:
                        migration_method(cursor)
                        cursor.execute(
                            f'INSERT INTO {self.version_table} (version, description) VALUES (?, ?)',
                            (version, f'Migration to version {version}')
                        )
                        conn.commit()
                        logger.info(f"Successfully migrated to version {version}")
                    except Exception as e:
                        logger.error(f"Failed to migrate to version {version}: {e}")
                        conn.rollback()
                        raise
                else:
                    logger.warning(f"No migration method found for version {version}")
            
            return True
    
    def migrate_to_v1(self, cursor: sqlite3.Cursor):
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
    
    def migrate_to_v2(self, cursor: sqlite3.Cursor):
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        logger.info(f"Current columns in users: {column_names}")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users_new (
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

        select_cols = []
        insert_cols = []

        base_columns = ['chat_id', 'username', 'first_name', 'last_name', 'name', 
                       'deck', 'city', 'created_at', 'last_activity']
        
        for col in base_columns:
            if col in column_names:
                select_cols.append(col)
                insert_cols.append(col)

        if 'last_daily_card_date' in column_names:
            select_cols.append('last_daily_card_date')
            insert_cols.append('last_cards_daily_date')
        elif 'last_cards_daily_date' in column_names:
            select_cols.append('last_cards_daily_date')
            insert_cols.append('last_cards_daily_date')

        if select_cols:
            select_sql = f'''
                INSERT INTO users_new ({', '.join(insert_cols)})
                SELECT {', '.join(select_cols)}
                FROM users
            '''
            logger.info(f"Copying data with SQL: {select_sql}")
            cursor.execute(select_sql)

        cursor.execute('DROP TABLE IF EXISTS users')
        cursor.execute('ALTER TABLE users_new RENAME TO users')

        cursor.execute("DROP TABLE IF EXISTS session_data")
    
    def migrate_to_v3(self, cursor: sqlite3.Cursor):
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required for migration v3")

        cursor.execute('SELECT chat_id, first_name, last_name, username FROM users')
        users = cursor.fetchall()
        
        total_users = len(users)
        logger.info(f"Starting user data validation for {total_users} users")
        
        updated_count = 0
        error_count = 0
        
        for i, user in enumerate(users, 1):
            chat_id = user['chat_id']
            db_first_name = user['first_name'] or ''
            db_last_name = user['last_name'] or ''
            db_username = user['username'] or ''
            
            try:
                response = self._get_chat_member_info(chat_id)
                
                if response and response.get('ok'):
                    result = response.get('result', {})
                    user_info = result.get('user', {})
                    
                    api_first_name = user_info.get('first_name', '') or ''
                    api_last_name = user_info.get('last_name', '') or ''
                    api_username = user_info.get('username', '') or ''

                    needs_update = (
                        api_first_name != db_first_name or
                        api_last_name != db_last_name or
                        api_username != db_username
                    )
                    
                    if needs_update:
                        cursor.execute('''
                            UPDATE users 
                            SET first_name = ?, 
                                last_name = ?, 
                                username = ?,
                                last_activity = CURRENT_TIMESTAMP
                            WHERE chat_id = ?
                        ''', (
                            api_first_name,
                            api_last_name,
                            api_username,
                            chat_id
                        ))
                        
                        updated_count += 1
                        logger.info(f"Updated user {chat_id}: "
                                  f"first_name: {db_first_name}->{api_first_name}, "
                                  f"last_name: {db_last_name}->{api_last_name}, "
                                  f"username: {db_username}->{api_username}")

                    if i % 10 == 0:
                        logger.info(f"Progress: {i}/{total_users} users checked, "
                                  f"{updated_count} updated, {error_count} errors")

                time.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error checking user {chat_id}: {e}")
                continue
        
        logger.info(f"User data validation completed: "
                   f"{total_users} users checked, "
                   f"{updated_count} updated, "
                   f"{error_count} errors")
    
    def _get_chat_member_info(self, chat_id: str) -> Optional[dict]:

        try:
            url = f"https://api.telegram.org/bot{self.BOT_TOKEN}/getChatMember"
            params = {
                'chat_id': chat_id,
                'user_id': chat_id
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for user {chat_id}: {e}")
            return None
        except ValueError as e:
            logger.error(f"Invalid JSON response for user {chat_id}: {e}")
            return None
        
    def _drop_column(self, cursor: sqlite3.Cursor, column_name: str):
        cursor.execute("PRAGMA table_info(users)")
        columns_info = cursor.fetchall()

        select_columns = []
        create_columns = []
        
        for col in columns_info:
            col_name = col[1]
            col_type = col[2]
            
            if col_name == column_name:
                continue
            elif col_name == 'last_daily_card_date':
                select_columns.append('last_daily_card_date as last_cards_daily_date')
                create_columns.append('last_cards_daily_date TEXT')
            else:
                select_columns.append(col_name)
                create_columns.append(f'{col_name} {col_type}')

        create_sql = f'''
            CREATE TABLE users_new (
                {', '.join(create_columns)}
            )
        '''
        cursor.execute(create_sql)

        if select_columns:
            select_sql = f'''
                INSERT INTO users_new 
                SELECT {', '.join(select_columns)} 
                FROM users
            '''
            cursor.execute(select_sql)

        cursor.execute('DROP TABLE users')
        cursor.execute('ALTER TABLE users_new RENAME TO users')
    
    def _rename_column_via_recreation(self, cursor: sqlite3.Cursor, old_name: str, new_name: str):
        cursor.execute("PRAGMA table_info(users)")
        columns_info = cursor.fetchall()

        select_columns = []
        create_columns = []
        
        for col in columns_info:
            col_name = col[1]
            col_type = col[2]
            
            if col_name == old_name:
                select_columns.append(f'{old_name} as {new_name}')
                create_columns.append(f'{new_name} {col_type}')
            else:
                select_columns.append(col_name)
                create_columns.append(f'{col_name} {col_type}')

        create_sql = f'''
            CREATE TABLE users_new (
                {', '.join(create_columns)}
            )
        '''
        cursor.execute(create_sql)

        select_sql = f'''
            INSERT INTO users_new 
            SELECT {', '.join(select_columns)} 
            FROM users
        '''
        cursor.execute(select_sql)

        cursor.execute('DROP TABLE users')
        cursor.execute('ALTER TABLE users_new RENAME TO users')