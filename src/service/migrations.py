import sqlite3
import logging

logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.version_table = "__db_version"
        self.current_version = 2  
        
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