from typing import *
from . import buttons

def get_message_body(
    text: str,
    format: "Literal['markdown', 'html'] | None" = None,
    reply_to: "int | None" = None,
    notify: bool = True,
    keyboard: "List[List[buttons.Button]] | buttons.KeyboardBuilder | None" = None,
    attachments: "List[Attachment] | None" = None
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
        if isinstance(keyboard, buttons.KeyboardBuilder):
            keyboard = keyboard.to_list()
        body['attachments'] = [{
            'type': 'inline_keyboard',
            'payload': {'buttons': keyboard}
        }]
    
    if attachments:
        if 'attachments' not in body:
            body['attachments'] = []
        for at in attachments or []:
            # todo: implement all attachment types in https://github.com/max-messenger/max-bot-api-client-ts/blob/main/examples/attachments-bot.ts
            assert hasattr(at, 'as_dict'), 'Attachment must be an image, a video, an audio or a file'
            body['attachments'].append(at.as_dict())

    if attachments == []:
        body['attachments'] = []

    return body