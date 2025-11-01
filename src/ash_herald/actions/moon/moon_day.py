import os, time, requests, logging
import ash_herald.utils.utils as utils
from telebot import types

logger = logging.getLogger('MOON_DAY')

async def moon_day(bot, call, session):
    chat_id = await utils.get_chat_id(call)
    url = os.getenv("MOON_API_URL")
    
    try:
        loading_msg1 = await bot.send_message(
            chat_id, 
            "☽ <i>Взгляд скользит по ночной выси...</i> ☾",   
            parse_mode="HTML"
        )
        time.sleep(1.5)

        loading_msg2 = await bot.send_message(
            chat_id, 
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

            logger.info(f"User: {session.name}, moon_day: {moon_age}\n{moon_phase}\n{illumination}\n{moon_zodiac}")
        
            message_text = (
                f"<b>╔═══════✦ ⋆☽ {moon_emoji} ☾⋆ ✦═══════╗</b>\n"
                f"  ✧ Фаза луны ⋄ {moon_phase}\n"
                f"  ✧ Лунный день ⋄ {moon_age}\n"
                f"  ✧ Луна в знаке ⋄ {moon_zodiac}\n"
                f"  ✧ Видимость луны ⋄ {illumination}%\n"
                f"<b>╚═══════✦ ⋆☽ {moon_emoji} ☾⋆ ✦═══════╝</b>"
            )
            
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("⛧ К истокам ⛧", callback_data="thanks")
            markup.add(btn1)

            await bot.send_message(chat_id, message_text, parse_mode="HTML", reply_markup=markup)
            logger.info(f"User: {session.name}, action: moon_day sent")

            try:
                await bot.delete_message(chat_id, loading_msg1.message_id)
                await bot.delete_message(chat_id, loading_msg2.message_id)
            except:
                pass
                
        else:
            logger.error(f"User: {session.name}, API error {response.status_code}")
            await bot.send_message(
                chat_id, 
                "  ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅\n"
                "       <i>Лунные скрижали покрыты пеленой,</i>\n"
                " <i>небесные силы временно безмолвствуют...</i>\n\n"
                "  ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"User: {session.name}, error in moon_day: {e}")
        await bot.send_message(
            chat_id, 
            "  ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅\n"
            "       <i>Небеса закрыли свои врата...</i>\n"
            "<i>Луна скрылась за облаками. Попробуй позже.</i>"
            "  ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ ⋆ ⋅ ✧ ⋅ 🜏 ⋅",
            parse_mode="HTML"
        )