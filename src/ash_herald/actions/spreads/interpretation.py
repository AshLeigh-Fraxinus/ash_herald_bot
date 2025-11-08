import random
import os
import logging
import time

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('INTERPRETATION')
client = Groq(api_key=os.getenv("GROQ_API_KEY"))  

system_settings = {
    "role": "system", 
    "content": """Дай толкование каждой полученной карте в контексте вопроса, не более 350 символов на каждую карту. 
    В конце сообщения сделай общий вывод на основе истрактованного расклада, сформулируй краткий ответ на вопрос пользователя.
    Не пиши в сообщении "общий вывод" и другие вводные конструкции - сразу содержимое.
    Используй архаичные славянские обороты, но оставайся понятным и доступным. 
    Перевёрнутые карты — не противоположность, а искажённое проявление энергии. 
    Запрещены иероглифы, текст на других языках кроме русского"""}

NO_ANSWER = [
    ("Из колоды выпадает карта...\nЭто Верховная жрица, привратница тайн.\nВопрос оказался сложнее, чем ожидалось."),
    ("Из колоды выпадает карта...\nЭто Луна, воплощение сокрытого и туманного.\nВопрос оказался сложнее, чем ожидалось.")]

async def make_llm_request(question, cards_description):
    user_prompt = f"{question} {cards_description}"
    user_settings = {"role": "user", "content": user_prompt}

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[system_settings, user_settings],
                temperature=0.7,
                max_tokens=500,
                timeout=15
            )
            interpretation = response.choices[0].message.content
            return interpretation

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < 2:
                time.sleep(2)
                continue
    
    selected = random.choice(NO_ANSWER)
    logger.warning(f"All attempts failed, returning fallback response")
    return selected


async def get_interpretation(question, cards):
    cards_description = []

    for i, card in enumerate(cards, 1):
        if isinstance(card, dict):
            card_name = card.get('name', 'Неизвестная карта')
            if card['position'] == 'upright': position =  'прямое положение'
            if card['position'] == 'reversed': position = 'перевёрнутое положение'
            cards_description.append(f"{i}. {card_name} {position}")
        else:
            cards_description.append(f"{i}. {str(card)}")
    return await make_llm_request(question=question, cards_description=cards_description)
