from .types import *
from typing import *
from .buttons import *


def get_message_body(
    text: str,
    format: "Literal['markdown', 'html', 'default'] | None" = None,
    reply_to: "int | None" = None,
    notify: bool = True,
    keyboard: "List[List[Button]] | None" = None,
) -> dict:
    '''
    Returns the body of the message as json.
    '''
    body = {
        "text": text,
        "format": format,
        "notify": notify
    }

    # replying
    if reply_to:
        body['link'] = {
            "type": 'reply',
            "mid": reply_to
        }

    # keyboard
    if keyboard:
        body['attachments'] = [{
            'type': 'inline_keyboard',
            'payload': {'buttons': keyboard}
        }]

    return body