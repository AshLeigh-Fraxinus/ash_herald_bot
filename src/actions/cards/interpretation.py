import random, os, logging, time, sqlite3

from groq import Groq
from dotenv import load_dotenv
from actions.cards.db_interpretation import DatabaseManager

load_dotenv()

logger = logging.getLogger('H.interpretator')
client = Groq(api_key=os.getenv("GROQ_API_KEY"))  
db_manager = DatabaseManager()

system_settings = {
    "role": "system", 
    "content": """Дай толкование каждой полученной карте в контексте вопроса: одно-два предложения, не длиннее 250 символов на карту.
    Говори о человеке и о том деле, про которое спросили: о его состоянии и о том, чем дело обернётся.
    Обращайся к спрашивающему на "ты". Если в вопросе назван по имени другой человек, о нём говори в третьем лице, а обращение на "ты" не используй.
    Не придумывай того, чего нет в вопросе: ни людей, ни должностей, ни сумм, ни сроков, ни событий. О чём не знаешь - не говори вовсе.
    Советов не давай: карта говорит о том, что есть, а не о том, что делать.
    Если карта одна - никакого итога не пиши вовсе, самого толкования достаточно.
    Если в запросе есть исходный расклад с его толкованием и дополнительная карта - толкуй только дополнительную карту, прежние карты заново не пересказывай. Прежнее толкование держи в уме как контекст и ответь на уточняющий вопрос.
    Если карт несколько - последним абзацем одним предложением ответь на вопрос определённо: да, нет или при каком условии.
    Начинай этот абзац сразу с того, что происходит с человеком, или с прямого ответа на вопрос. Ответ делай содержательным, а не одним словом.
    В этом абзаце говори о человеке и его деле, карты в нём не упоминай.
    Словами-метками текст не размечай: никаких "Ответ", "Вывод", "Итог", "Совет" - сразу содержание.
    Про сам расклад и про карты как инструмент не рассуждай - говори только о человеке и его деле.
    Пиши ясным современным русским языком, плавно и без нагромождений. Один живой образ на карту уместен, развёрнутые картины - нет.
    Не используй устаревшие, книжные и усечённые формы слов, не придумывай слов.
    Перевёрнутую карту называй "перевёрнутая", а не "обратна".
    Перевёрнутые карты — не противоположность, а искажённое проявление энергии. 
    Разметку не используй совсем: ни звёздочек, ни решёток, ни HTML-тегов - только обычный текст.
    Запрещены иероглифы, текст на других языках кроме русского"""}

async def make_llm_request(question, cards_description):
    user_prompt = f"{question} {cards_description}"
    user_settings = {"role": "user", "content": user_prompt}

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model='openai/gpt-oss-120b',
                messages=[system_settings, user_settings],
                temperature=0.7,
                max_tokens=1500,
                extra_body={'reasoning_effort': 'low'},
                timeout=15
            )
            interpretation = response.choices[0].message.content
            if not interpretation or not interpretation.strip():
                raise ValueError(f'empty response, finish_reason: "{response.choices[0].finish_reason}"')
            return interpretation

        except Exception as e:
            logger.error(f'Attempt _{attempt + 1}_ failed with error: "{e}"')
            if attempt < 2:
                time.sleep(2)
                continue

    fallback_response = db_manager.get_fallback_interpretation()
    logger.warning("All LLM attempts failed, returning database interpretation")
    return fallback_response


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

async def get_direct_interpretation(cards):
    interpretations = []
    
    for i, card in enumerate(cards, 1):
        if isinstance(card, dict):
            card_name = card.get('name', 'Неизвестная карта')
            position = card.get('position', 'upright')
            
            db_interpretation = db_manager.get_card_interpretation(card_name, position)
            
            if db_interpretation:
                position_text = 'прямое' if position == 'upright' else 'перевёрнутое'
                interpretations.append(f"{card_name} ({position_text}): {db_interpretation}")
            else:
                interpretations.append(f"{card_name} - трактовка не найдена")
        else:
            interpretations.append(f"{str(card)} - неизвестная карта")
    
    return "\n".join(interpretations)