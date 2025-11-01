import logging

logger = logging.getLogger('UTILS')

def get_username_and_names(message):
    username, first_name, last_name = ('', '', '')
    if message is None:
        logger.error(f'Empty "message" to get_username_and_names passed')
        return username, first_name, last_name
    
    if hasattr(message, 'chat') and message.chat is not None:
        if hasattr(message.chat, 'username') and message.chat.username is not None:
            username = message.chat.username
        if hasattr(message.chat, 'first_name') and message.chat.first_name is not None:
            first_name = message.chat.first_name
        if hasattr(message.chat, 'last_name') and message.chat.last_name is not None:
            last_name = message.chat.last_name

    if hasattr(message, 'from_user') and message.from_user is not None:
        if hasattr(message.from_user, 'username') and message.from_user.username is not None:
            username = message.from_user.username
        if hasattr(message.from_user, 'first_name') and message.from_user.first_name is not None:
            first_name = message.from_user.first_name
        if hasattr(message.from_user, 'last_name') and message.from_user.last_name is not None:
            last_name = message.from_user.last_name

    if hasattr(message, 'message') and message.message is not None:
        if hasattr(message.message, 'chat') and message.message.chat is not None:
            if hasattr(message.message.chat, 'username') and message.message.chat.username is not None:
                username = message.message.chat.username
            if hasattr(message.message.chat, 'first_name') and message.message.chat.first_name is not None:
                first_name = message.message.chat.first_name
            if hasattr(message.message.chat, 'last_name') and message.message.chat.last_name is not None:
                last_name = message.message.chat.last_name
    
    return username, first_name, last_name

async def get_chat_id(message):
    if message is None:
        logger.error(f'Empty "message" to get_chat_id passed')
        return ""

    if hasattr(message, 'chat') and message.chat is not None:
        if hasattr(message.chat, 'id') and message.chat.id is not None:
            return str(message.chat.id)

    if hasattr(message, 'message') and message.message is not None:
        if hasattr(message.message, 'chat') and message.message.chat is not None:
            if hasattr(message.message.chat, 'id') and message.message.chat.id is not None:
                return str(message.message.chat.id)

    if hasattr(message, 'from_user') and message.from_user is not None:
        return str(message.from_user.id)
    
    logger.error(f'Unable to get chat_id from: {message}')
    return ""

def get_text(message):
    if message is None:
        logger.error(f'Empty "message" to get_text passed')
        return ""
    if hasattr(message, 'text') and message.text is not None:
        return str(message.text)
    logger.error(f'Unable to get text from: {message}')
    return ""

def get_clean_name(username, first_name, last_name):
    def clean_name(name):
        if not name:
            return ""
        return ''.join(char for char in name if char.isalpha() or char.isspace() or char.isdigit())
    clean_first = clean_name(first_name)
    clean_last = clean_name(last_name)

    if len(username) > 0:
        return username
    if len(last_name) > 0:
        return clean_first + " " + clean_last
    return clean_first 

def no_newline(str):
    str = str.replace('\n', '')
    str = str.replace('\r', '')
    return str