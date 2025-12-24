import sqlite3
import logging

logger = logging.getLogger('H.db_interpretation')

class DatabaseManager:
    def __init__(self, db_path: str = "database/tarot.db"):
        self.db_path = db_path

    def get_card_interpretation(self, card_name, position):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                column = 'daily_card_is_upright' if position == 'upright' else 'daily_card_is_reversed'
                
                cursor.execute(f'''
                    SELECT {column} FROM tarot_cards 
                    WHERE name = ? OR russian_name = ?
                ''', (card_name, card_name))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Database error for card {card_name}: {e}")
            return None

    def get_fallback_interpretation(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT daily_card_is_upright FROM tarot_cards 
                    ORDER BY RANDOM() LIMIT 1
                ''')
                result = cursor.fetchone()
                logger.info(result)
                if result:
                    interpretation = result[0]
                    return f"{interpretation}..."
                return "Карты пока хранят молчание. Попробуйте задать вопрос позже."
                
        except Exception as e:
            logger.error(f"Fallback interpretation error: {e}")
            return "Внутренняя ошибка при обращении к картам."