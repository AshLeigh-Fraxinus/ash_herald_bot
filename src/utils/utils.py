import logging

logger = logging.getLogger('H.utils')

def get_username_and_names(message, return_type='all'):
    if message is None:
        logger.error('Empty "message" passed to get_username_and_names')
        if return_type == 'first_name':
            return ''
        return '', '', ''
    
    username, first_name, last_name = '', '', ''
    sources = [
        (getattr(message, 'chat', None), ['username', 'first_name', 'last_name']),
        (getattr(message, 'from_user', None), ['username', 'first_name', 'last_name']),
        (getattr(getattr(message, 'message', None), 'chat', None), ['username', 'first_name', 'last_name'])
    ]
    
    for source, fields in sources:
        if source:
            username = username or getattr(source, fields[0], '')
            first_name = first_name or getattr(source, fields[1], '')
            last_name = last_name or getattr(source, fields[2], '')
    
    if return_type == 'username':
        return username or ''
    elif return_type == 'first_name':
        return first_name or ''
    elif return_type == 'last_name':
        return last_name or ''
    else:
        return username or '', first_name or '', last_name or ''

async def get_chat_id(message):
    if message is None:
        return ""

    sources = [
        getattr(message, 'chat', None),
        getattr(getattr(message, 'message', None), 'chat', None),
        getattr(message, 'from_user', None)
    ]
    for source in sources:
        if source and hasattr(source, 'id') and source.id:
            return str(source.id)
    logger.error(f'Unable to get chat_id from: "{message}"')
    return ""

def get_text(message):
    if message and hasattr(message, 'text') and message.text:
        return str(message.text)
    logger.error(f'Unable to get text from: "{message}"')
    return ""

def get_clean_name(username, first_name, last_name):
    def clean_name(name):
        if not name:
            return ""
        return ''.join(char for char in name if char.isalpha() or char.isspace() or char.isdigit() or char == '_')
    
    if username:
        return username

    clean_first = clean_name(first_name)
    clean_last = clean_name(last_name)

    if len(last_name) > 0:
        return clean_first + " " + clean_last
    return clean_first 

def no_newline(text):
    if hasattr(text, 'replace'):
        return text.replace('\n', ' ').replace('\r', ' ')
    elif hasattr(text, 'text'):
        return text.text.replace('\n', ' ').replace('\r', ' ')
    else:
        return str(text).replace('\n', ' ').replace('\r', ' ')