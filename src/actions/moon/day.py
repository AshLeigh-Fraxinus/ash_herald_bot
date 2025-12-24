import os, time, requests, logging
from telebot import types
from handlers.handle_common import main_keyboard
from utils.keyboards import thanks_keyboard

logger = logging.getLogger('H.moon_day')

async def moon_day(bot, session):
    url = os.getenv("MOON_API_URL")
    
    try:
        loading_msg1 = await bot.send_message(
            session.chat_id, 
            "☽ <i>Взгляд скользит по ночной выси...</i> ☾",   
            parse_mode="HTML"
        )
        time.sleep(1.5)

        loading_msg2 = await bot.send_message(
            session.chat_id, 
            "✣ <i>Сверяюсь с гримуаром светил...</i> ✣", 
            parse_mode="HTML"
        )
        time.sleep(1.5)

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()  
            current_state = data["CurrentState"]

            moon_age = current_state["MoonDays"]
            moon_phase = current_state["Phase"]["NameLocalized"]
            moon_emoji = current_state["Phase"]["Emoji"]
            illumination = current_state["Illumination"]
            moon_zodiac = current_state["Zodiac"]["NameLocalized"]

            logger.debug(f"moon age: {moon_age}, moon phaze: {moon_phase}, illumination: {illumination}, zodiac: {moon_zodiac}")

            await bot.send_message(
                session.chat_id, 
                text = (
                    f"<b>══════✦ ⋆☽ {moon_emoji} ☾⋆ ✦══════</b>\n\n"
                    f"✧ Фаза луны  ⋆  {moon_phase}\n"
                    f"✧ Лунный день  ⋆  {moon_age}\n"
                    f"✧ Луна в знаке  ⋆  {moon_zodiac}\n"
                    f"✧ Видимость луны  ⋆  {illumination}%"
                ), 
                parse_mode="HTML", 
                reply_markup=thanks_keyboard()
            )
            logger.info(f'"{session.username}" received: "moon_day"')

            try:
                await bot.delete_message(session.chat_id, loading_msg1.message_id)
                await bot.delete_message(session.chat_id, loading_msg2.message_id)
            except:
                pass
                
        else:
            logger.error(f'"{session.username}" got API error "{response.status_code}"')
            await bot.send_message(
                session.chat_id, 
                text=(
                    "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ 🜏 ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
                    "       <i>Лунные скрижали покрыты пеленой,</i>\n"
                    " <i>небесные силы временно безмолвствуют...</i>\n\n"
                ),
                parse_mode="HTML",
                reply_markup=main_keyboard()
            )
            
    except Exception as e:
        logger.error(f'"{session.username}" got error in moon_day: "{e}"')
        await bot.send_message(
            session.chat_id, 
            "⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ 🜏 ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ \n"
            "       <i>Небеса закрыли свои врата...</i>\n"
            "<i>Луна скрылась за облаками. Попробуй позже.</i>",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )