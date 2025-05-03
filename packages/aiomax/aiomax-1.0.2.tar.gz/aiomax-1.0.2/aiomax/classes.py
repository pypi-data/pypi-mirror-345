from .utils import get_message_body
from typing import *
from . import buttons


class BotCommand:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    
    def as_dict(self):
        return {
            "name": self.name, "description": self.description
        }


class User:
    def __init__(self,
        user_id: int,
        first_name: str,
        name: str,
        is_bot: bool,
        last_activity_time: int,
        last_name: "str | None" = None,
        username: "str | None" = None,
        description: "str | None" = None,
        avatar_url: "str | None" = None,
        full_avatar_url: "str | None" = None,
        commands: "List[BotCommand] | None" = None,
        last_access_time: "int | None" = None,
        is_owner: "bool | None" = None,
        is_admin: "bool | None" = None,
        join_time: "int | None" = None,
        permissions: "List[str] | None" = None

    ):
        self.user_id: int = user_id
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.name: str = name
        self.username: "str | None" = username
        self.is_bot: bool = is_bot
        self.last_activity_time: int = last_activity_time
        self.description: "str | None" = description
        self.avatar_url: "str | None" = avatar_url
        self.full_avatar_url: "str | None" = full_avatar_url
        self.commands: "List[BotCommand] | None" = [
            BotCommand(**i) for i in commands
        ] if commands else None
        self.last_access_time: "int | None" = last_access_time
        self.is_owner: "bool | None" = is_owner
        self.is_admin: "bool | None" = is_admin
        self.join_time: "int | None" = join_time
        self.permissions: "List[str] | None" = permissions


    def __repr__(self):
        return f"{type(self).__name__}(user_id={self.user_id!r}, name={self.name!r})"


    def __eq__(self, other):
        return self.user_id == other.user_id


    @staticmethod
    def from_json(data: dict) -> "User | None":
        if data == None: return None

        return User(**data)


class Attachment:
    def __init__(self, type: str):
        self.type: str = type


    @staticmethod
    def from_json(data: dict) -> "Attachment | None":
        if data['type'] == 'image':
            return PhotoAttachment.from_json(data)
        elif data['type'] == 'video':
            return VideoAttachment.from_json(data)
        elif data['type'] == 'audio':
            return AudioAttachment.from_json(data)
        elif data['type'] == 'file':
            return FileAttachment.from_json(data)
        elif data['type'] == 'sticker':
            return StickerAttachment.from_json(data)
        elif data['type'] == 'contact':
            return ContactAttachment.from_json(data)
        elif data['type'] == 'share':
            return ShareAttachment.from_json(data)
        elif data['type'] == 'location':
            return LocationAttachment.from_json(data)
        elif data['type'] == 'inline_keyboard':
            return InlineKeyboardAttachment.from_json(data)
        else:
            raise Exception(f"Unknown attachment type: {data['type']}")


class MediaPayload:
    def __init__(self,
        token: str,
        url: "str | None" = None,
    ):
        self.url: "str | None" = url
        self.token: str = token


    @staticmethod
    def from_json(data: dict) -> "MediaPayload | None":
        return MediaPayload(url=data.get('url'), token=data.get('token'))


class StickerPayload:
    def __init__(self,
        url: str,
        code: str,
    ):
        self.url: str = url
        self.code: str = code


    @staticmethod
    def from_json(data: dict) -> "StickerPayload | None":
        return StickerPayload(data['url'], data['code'])


class ContactPayload:
    def __init__(self,
        vcf_info: "str | None" = None,
        max_info: "User | None" = None,
    ):
        self.vcf_info: "str | None" = vcf_info
        self.max_info: "User | None" = max_info


    @staticmethod
    def from_json(data: dict) -> "ContactPayload | None":
        return ContactPayload(data['vcf_info'], data['max_info'])


class PhotoPayload(MediaPayload):
    def __init__(self,
        token: str,
        url: "str | None" = None,
        photo_id: "int | None" = None
    ):
        super().__init__(url=url, token=token)
        self.photo_id: "int | None" = photo_id

    
    @staticmethod
    def from_json(data: dict) -> "PhotoPayload | None":
        return PhotoPayload(url=data.get('url'), token=data.get('token'), photo_id=data.get('photo_id'))


class PhotoAttachment(Attachment):
    def __init__(self,
        payload: PhotoPayload
    ):
        super().__init__("image")
        self.payload: PhotoPayload = payload


    @staticmethod
    def from_json(data: dict) -> "PhotoAttachment | None":
        return PhotoAttachment(
            PhotoPayload.from_json(data['payload'])
        )
    
    
    def as_dict(self):
        return {
            'type': self.type,
            'payload': {'token': self.payload.token}
        }


class VideoAttachment(Attachment):
    def __init__(self,
        payload: MediaPayload,
        thumbnail: "str | None" = None,
        width: "int | None" = None,
        height: "int | None" = None,
        duration: "int | None" = None
    ):
        super().__init__("video")
        self.payload: MediaPayload = payload
        self.thumbnail: "str | None" = thumbnail
        self.width: "int | None" = width
        self.height: "int | None" = height
        self.duration: "int | None" = duration

    
    @staticmethod
    def from_json(data: dict) -> "VideoAttachment | None":
        return VideoAttachment(
            MediaPayload.from_json(data['payload']),
            data.get('thumbnail', None),
            data.get('width', None),
            data.get('height', None),
            data.get('duration', None),
        )
    
    
    def as_dict(self):
        return {
            'type': self.type,
            'payload': {'token': self.payload.token}
        }


class AudioAttachment(Attachment):
    def __init__(self,
        payload: MediaPayload,
        transcription: "str | None" = None
    ):
        super().__init__("audio")
        self.payload: MediaPayload = payload
        self.transcription: "str | None" = transcription


    @staticmethod
    def from_json(data: dict) -> "AudioAttachment | None":
        return AudioAttachment(
            MediaPayload.from_json(data['payload']),
            data.get('transcription', None)
        )
    
    
    def as_dict(self):
        return {
            'type': self.type,
            'payload': {'token': self.payload.token}
        }


class FileAttachment(Attachment):
    def __init__(self,
        payload: MediaPayload,
        filename: "str | None" = None,
        size: "int | None" = None
    ):
        super().__init__("file")
        self.payload: MediaPayload = payload
        self.filename: "str | None" = filename
        self.size: "int | None" = size


    @staticmethod
    def from_json(data: dict) -> "FileAttachment | None":
        return FileAttachment(
            MediaPayload.from_json(data['payload']),
            data.get('filename'),
            data.get('size')
        )
    
    
    def as_dict(self):
        return {
            'type': self.type,
            'payload': {'token': self.payload.token}
        }


class StickerAttachment(Attachment):
    def __init__(self,
        payload: StickerPayload,
        width: "int | None" = None,
        height: "int | None" = None
    ):
        super().__init__("sticker")
        self.payload: StickerPayload = payload
        self.width: int = width
        self.height: int = height

    
    @staticmethod
    def from_json(data: dict) -> "StickerAttachment | None":
        return StickerAttachment(
            StickerPayload.from_json(data['payload']),
            data.get('width', None),
            data.get('height', None)
        )


class ContactAttachment(Attachment):
    def __init__(self,
        payload: ContactPayload,
    ):
        super().__init__("contact")
        self.payload: ContactPayload = payload


    @staticmethod
    def from_json(data: dict) -> "ContactAttachment | None":
        return ContactAttachment(
            ContactPayload.from_json(data['payload'])
        )


class ShareAttachment(Attachment):
    def __init__(self,
        payload: "MediaPayload | None",
        url: "str | None" = None,
        title: "str | None" = None,
        description: "str | None" = None,
        image_url: "str | None" = None,
    ):
        super().__init__("share")
        self.url: "str | None" = url
        self.payload: "MediaPayload | None" = payload
        self.title: "str | None" = title
        self.description: "str | None" = description
        self.image_url: "str | None" = image_url


    @staticmethod
    def from_json(data: dict) -> "ShareAttachment | None":
        return ShareAttachment(
            MediaPayload.from_json(data.get('payload', None)),
            data['payload'].get('url', None),
            data.get('title', None),
            data.get('description', None),
            data.get('image_url', None),
        )


class LocationAttachment(Attachment):
    def __init__(self,
        latitude: float,
        longitude: float,
    ):
        super().__init__("location")
        self.latitude: float = latitude
        self.longitude: float = longitude


    @staticmethod
    def from_json(data: dict) -> "LocationAttachment | None":
        return LocationAttachment(
            data['latitude'],
            data['longitude']
        )


class InlineKeyboardAttachment(Attachment):
    def __init__(self,
        payload: List[List[buttons.Button]],
    ):
        super().__init__("inline_keyboard")
        self.payload: List[List[buttons.Button]] = payload


    @staticmethod
    def from_json(data: dict) -> "InlineKeyboardAttachment | None":
        return InlineKeyboardAttachment(
            [[buttons.Button.from_json(j) for j in i] for i in data['payload']['buttons']]
        )


class MessageRecipient:
    def __init__(self,
        chat_id: "int | None",
        chat_type: str
    ):
        self.chat_id: "int | None" = chat_id
        self.chat_type: str = chat_type

    def __repr__(self):
        return f"{type(self).__name__}(chat_id={self.chat_id!r}, chat_type={self.chat_type!r})"
    
    def __eq__(self, other):
        return self.chat_id == other.chat_id

    @staticmethod
    def from_json(data: dict) -> "MessageRecipient":
        if data == None: return None

        return MessageRecipient(
            chat_id = data["chat_id"],
            chat_type = data["chat_type"]
        )
    

class Markup:
    def __init__(self,
        type: Literal[
            'strong', 'emphasized', 'monospaced', 'link', 'strikethrough',
            'underline', 'user_mention', 'heading', 'highlighted'
        ],
        start: int,
        length: int,
        user_link: "str | None" = None,
        user_id: "int | None" = None,
        url: "str | None" = None
    ):
        '''
        A markup element

        :param type: Markup type
        :param start: Start position
        :param length: Length
        :param user_link: Username. `None` if markup type is not `user_link`
        :param user_id: User ID. `None` if markup type is not `user_link`
        :param url: URL. `None` if markup type is not `link`
        '''
        self.type: Literal[
            'strong', 'emphasized', 'monospaced', 'link', 'strikethrough',
            'underline', 'user_mention', 'heading', 'highlighted'
        ] = type
        self.start: int = start
        self.length: int = length

        self.user_link: "str | None" = user_link
        self.user_id: "int | None" = user_id
        self.url: "str | None" = url


    @staticmethod
    def from_json(data: dict) -> "Markup | None":
        if data == None: return None

        if data['type'] == 'user_mention':
            return Markup(
                data['type'], data['from'], data['length'],
                user_link=data.get('user_link', None), user_id=data.get('user_id', None)
            )
        elif data['type'] == 'link':
            return Markup(
                data['type'], data['from'], data['length'], url=data['url']
            )

        return Markup(data['type'], data['from'], data['length'])


class MessageBody:
    def __init__(self,
        mid: str,
        seq: int,
        text: "str | None",
        attachments: "List[Attachment] | None",
        markup: "List[Markup] | None" = None
    ):
        self.message_id: str = mid
        self.seq: int = seq
        self.text: "str | None" = text
        self.attachments: "List[Attachment] | None" = attachments
        self.markup: "List[Markup] | None" = markup


    @staticmethod
    def from_json(data: dict) -> "MessageBody":
        if data == None: return None

        return MessageBody(
            mid = data["mid"],
            seq = data["seq"],
            text = data["text"],
            attachments = [Attachment.from_json(x) for x in data.get('attachments', [])],
            markup = [Markup.from_json(x) for x in data.get('markup', [])]
        )


class LinkedMessage:
    def __init__(self,
        type: str,
        message: MessageBody,
        sender: User,
        chat_id: "int | None" = None,
    ):
        self.type: str = type
        self.message: MessageBody = message
        self.sender: User = sender
        self.chat_id: "int | None" = chat_id


    @staticmethod
    def from_json(data: dict) -> "LinkedMessage":
        if data == None: return None
            
        return LinkedMessage(
            type = data["type"],
            message = MessageBody.from_json(data["message"]),
            sender = User.from_json(data.get('sender', None)),
            chat_id = data.get('chat_id', None),
        )


class Message:
    def __init__(self,
        recipient: MessageRecipient,
        body: MessageBody,
        timestamp: float,
        sender: User,
        link: "LinkedMessage | None" = None,
        views: "int | None" = None,
        url: "str | None" = None,
        bot = None
    ):
        self.recipient: MessageRecipient = recipient
        self.body: "MessageBody | None" = body
        self.timestamp: "float | None" = timestamp
        self.sender: "User | None" = sender
        self.link: "LinkedMessage | None" = link
        self.views: "int | None" = views
        self.url: "str | None" = url
        self.user_locale: "str | None" = None
        self.bot = bot

    def __repr__(self):
        return f"{type(self).__name__}(text={self.body.text!r})"

    def __str__(self):
        return self.body.text
    
    def __eq__(self, other):
        if not isinstance(other, Message):
            # return other.__eq__(self) # le excuse le me
            return False
        return self.id == other.id
    
    @property
    def id(self) -> str:
        return self.body.message_id
    
    @property
    def content(self) -> str:
        return self.body.text

    @staticmethod
    def from_json(data: dict) -> "Message":
        return Message(
            recipient = MessageRecipient.from_json(data.get('recipient')),
            body = MessageBody.from_json(data.get('body', None)),
            timestamp = data.get('timestamp', None),
            sender = User.from_json(data.get("sender", None)),
            link = LinkedMessage.from_json(data.get("link", None)),
            views = data.get("stat", {}).get("views", None),
            url = data.get("url", None)
        )


    async def send(self,
        text: str,
        format: "Literal['html', 'markdown', 'default'] | None" = 'default',
        notify: bool = True,
        disable_link_preview: bool = False,
        keyboard: "List[List[buttons.Button]] | buttons.KeyboardBuilder | None" = None,
        attachments: "List[Attachment] | None" = None
    ) -> "Message":
        '''
        Send a message to the chat that the message is sent.

        :param text: Message text. Up to 4000 characters
        :param format: Message format. Bot.default_format by default
        :param notify: Whether to notify users about the message. True by default.
        :param disable_link_preview: Whether to disable link preview. False by default
        :param keyboard: An inline keyboard to attach to the message
        :param attachments: List of attachments
        '''
        if self.bot == None:
            return
        return (await self.bot.send_message(
            text, chat_id=self.recipient.chat_id,
            format=format, notify=notify, disable_link_preview=disable_link_preview,
            keyboard=keyboard, attachments=attachments
        ))


    async def reply(self,
        text: str,
        format: "Literal['html', 'markdown', 'default'] | None" = 'default',
        notify: bool = True,
        disable_link_preview: bool = False,
        keyboard: "List[List[buttons.Button]] | buttons.KeyboardBuilder | None" = None,
        attachments: "List[Attachment] | None" = None
    ) -> "Message":
        '''
        Reply to this message.

        :param text: Message text. Up to 4000 characters
        :param format: Message format. Bot.default_format by default
        :param notify: Whether to notify users about the message. True by default.
        :param disable_link_preview: Whether to disable link preview. False by default
        :param keyboard: An inline keyboard to attach to the message
        :param attachments: List of attachments
        '''
        if self.bot == None:
            return
        return (await self.bot.send_message(
            text, chat_id=self.recipient.chat_id,
            format=format, notify=notify, disable_link_preview=disable_link_preview,
            keyboard=keyboard, attachments=attachments, reply_to=self.id
        ))
    
    async def edit(self,
        text: str,
        format: "Literal['html', 'markdown', 'default'] | None" = 'default',
        reply_to: "int | None" = None,
        notify: bool = True,
        keyboard: "List[List[buttons.Button]] | buttons.KeyboardBuilder | None" = None,
    ) -> "Message":
        '''
        Edit a message

        :param text: Message text. Up to 4000 characters
        :param format: Message format. Bot.default_format by default
        :param notify: Whether to notify users about the message. True by default.
        :param disable_link_preview: Whether to disable link preview. False by default
        :param keyboard: An inline keyboard to attach to the message
        :param attachments: List of attachments
        '''
        if self.bot == None:
            return
        return (await self.bot.edit_message(
            self.id, text,
            format=format, notify=notify,
            keyboard=keyboard, reply_to=reply_to
        ))
    
    async def delete(self):
        if self.bot == None:
            return
        return await self.bot.delete_message(
            self.id
        )


class BotStartPayload:
    def __init__(self,
        chat_id: int,
        user: User,
        payload: "str | None",
        user_locale: "str | None",
        bot = None
    ):
        self.chat_id: int = chat_id
        self.user: User = user
        self.payload: "str | None" = payload
        self.user_locale: "str | None" = user_locale
        self.bot = bot


    @staticmethod
    def from_json(data: dict, bot) -> "BotStartPayload":
        return BotStartPayload(
            chat_id = data["chat_id"],
            user = User.from_json(data["user"]),
            payload = data.get('payload', None),
            user_locale = data.get('user_locale', None),
            bot = bot,
        )
    
    async def send(self,
        text: str,
        format: "Literal['html', 'markdown', 'default'] | None" = 'default',
        notify: bool = True,
        disable_link_preview: bool = False,
        keyboard: "List[List[buttons.Button]] | buttons.KeyboardBuilder | None" = None,
        attachments: "List[Attachment] | None" = None
    ) -> "Message":
        '''
        Send a message to the chat where bot was started.

        :param text: Message text. Up to 4000 characters
        :param format: Message format. Bot.default_format by default
        :param notify: Whether to notify users about the message. True by default.
        :param disable_link_preview: Whether to disable link preview. False by default
        :param keyboard: An inline keyboard to attach to the message
        :param attachments: List of attachments
        '''
        if self.bot == None:
            return
        return (await self.bot.send_message(
            text, chat_id=self.chat_id,
            format=format, notify=notify, disable_link_preview=disable_link_preview,
            keyboard=keyboard, attachments=attachments
        ))
    
    

class CommandContext:
    def __init__(self,
        bot,
        message: Message,
        command_name: str,
        args: str
    ):
        self.bot = bot
        self.message: Message = message
        self.sender: User = message.sender
        self.recipient: MessageRecipient = message.recipient
        self.command_name: str = command_name
        self.args_raw: str = args
        self.args: List[str] = args.split()


    async def send(self,
        text: str,
        format: "Literal['html', 'markdown', 'default'] | None" = 'default',
        notify: bool = True,
        disable_link_preview: bool = False,
        keyboard: "List[List[buttons.Button]] | buttons.KeyboardBuilder | None" = None,
        attachments: "List[Attachment] | None" = None
    ) -> Message:
        '''
        Send a message to the chat that the user sent the command.

        :param text: Message text. Up to 4000 characters
        :param format: Message format. Bot.default_format by default
        :param notify: Whether to notify users about the message. True by default.
        :param disable_link_preview: Whether to disable link preview. False by default
        :param keyboard: An inline keyboard to attach to the message
        :param attachments: List of attachments
        '''
        return (await self.bot.send_message(
            text, chat_id=self.message.recipient.chat_id,
            format=format, notify=notify, disable_link_preview=disable_link_preview,
            keyboard=keyboard, attachments=attachments
        ))


    async def reply(self,
        text: str,
        format: "Literal['html', 'markdown', 'default'] | None" = 'default',
        notify: bool = True,
        disable_link_preview: bool = False,
        keyboard: "List[List[buttons.Button]] | buttons.KeyboardBuilder | None" = None,
        attachments: "List[Attachment] | None" = None
    ) -> Message:
        '''
        Reply to the message that the user sent.

        :param text: Message text. Up to 4000 characters
        :param format: Message format. Bot.default_format by default
        :param notify: Whether to notify users about the message. True by default.
        :param disable_link_preview: Whether to disable link preview. False by default
        :param keyboard: An inline keyboard to attach to the message
        :param attachments: List of attachments
        '''
        return (await self.bot.send_message(
            text, chat_id=self.message.recipient.chat_id,
            format=format, notify=notify, disable_link_preview=disable_link_preview,
            keyboard=keyboard, attachments=attachments, reply_to=self.message.id
        ))


class Handler:
    def __init__(
        self,
        call: Callable,
        filter: "Callable | None" = None,
    ):
        self.call = call
        self.filter = filter


class Image:
    def __init__(self,
        url: str,
    ):
        '''
        An image.

        :param url: Image URL
        '''
        self.url: str = url
    
    
    @staticmethod
    def from_json(data: dict) -> "Image | None":
        if data == None: return None

        return Image(**data)


class ImageRequestPayload:
    def __init__(self,
        url: "str | None" = None,
        token: "str | None" = None
    ):
        '''
        A payload with the info about an image or avatar to send to the bot.

        Only url or token must be specified.
        
        :param url: Image URL
        :param token: Attachment token generated by Bot.upload_image().token
        '''
        assert url or token, 'Token or URL must be specified'
        assert not (url and token), 'Token and URL cannot be specified at the same time'
        
        self.url: "str | None" = url
        self.token: "str | None" = token
    
    
    @staticmethod
    def from_json(data: dict) -> "ImageRequestPayload | None":
        if data == None: return None

        return ImageRequestPayload(**data)
    

    def as_dict(self):
        return { "url": self.url } if self.url else { "token": self.token }
    

class Chat:
    def __init__(self,
        chat_id: int,
        type: str,
        status: str,
        last_event_time: int,
        participants_count: int,
        is_public: bool,
        title: "str | None" = None,
        icon: "Image | None" = None,
        description: "str | None" = None,
        pinned_message: "Message | None" = None,
        owner_id: "int | None" = None,
        participants: "Dict[str, int] | None" = None,
        link: "str | None" = None,
        messages_count: "str | None" = None,
        chat_message_id: "str | None" = None,
        dialog_with_user: "User | None" = None,
    ):
        self.chat_id: int = chat_id
        self.type: str = type
        self.status: str = status
        self.last_event_time: int = last_event_time
        self.participants_count: int = participants_count
        self.title: "str | None" = title
        self.icon: "Image | None" = icon
        self.is_public: bool = is_public
        self.dialog_with_user: "User | None" = dialog_with_user
        self.description: "str | None" = description
        self.pinned_message: "Message | None" = pinned_message
        self.owner_id: "int | None" = owner_id
        self.participants: "Dict[int, int] | None" = {int(k): v for k, v in participants.items()} if participants else None
        self.link: "str | None" = link
        self.messages_count: "str | None" = messages_count
        self.chat_message_id: "str | None" = chat_message_id

    def __eq__(self, other):
        return self.chat_id == other.chat_id

    def __repr__(self):
        return f"{self.__class__.__name__}(chat_id={self.chat_id!r}, title={self.title!r})"

    @staticmethod
    def from_json(data: dict) -> "Chat | None":
        if data == None: return None

        return Chat(**data)
    

class Callback:
    def __init__(self,
        bot,
        timestamp: int,
        callback_id: str,
        user: User,
        user_locale: "str | None",
        payload: "str | None" = None
    ):
        self.bot = bot
        self.timestamp: int = timestamp
        self.callback_id: str = callback_id
        self.user: User = user
        self.payload: "str | None" = payload
        self.user_locale: "str | None" = user_locale

    
    @property
    def content(self) -> str:
        return self.payload
    

    async def answer(self,
        notification: "str | None" = None,
        text: "str | None" = None,
        format: "Literal['html', 'markdown', 'default'] | None" = 'default',
        notify: bool = True,
        keyboard: "List[List[buttons.Button]] | buttons.KeyboardBuilder | None" = None,
        attachments: "list[Attachment] | None" = None
    ):
        '''
        Answer the callback.

        :param notification: Notification to display to the user
        :param text: Message text. Up to 4000 characters
        :param format: Message format. Bot.default_format by default
        :param notify: Whether to notify users about the message. True by default.
        :param keyboard: An inline keyboard to attach to the message
        :param attachments: List of attachments
        '''
        assert notification != None or text != None or attachments,\
            'Either notification, text or attachments must be specified'
        body = {
            'notification': notification,
            'message': None
        }
        if text != None:
            format = self.bot.default_format if format == 'default' else format
            body['message'] = get_message_body(text, format, notify=notify, keyboard=keyboard, attachments=attachments)

        out = await self.bot.post(
            'https://botapi.max.ru/answers', params={'callback_id': self.callback_id},
            json=body
        )
        return await out.json()


    @staticmethod
    def from_json(data: dict, user_locale: "str | None" = None, bot = None) -> "Callback | None":
        if data == None: return None
        
        return Callback(
            bot,
            data['timestamp'],
            data['callback_id'],
            User.from_json(data['user']),
            user_locale,
            data.get('payload', None)
        )


class ChatCreatePayload:
    def __init__(self,
        timestamp: int,
        chat: Chat,
        message_id: "str | None" = None,
        start_payload: "str | None" = None
    ):
        '''
        Payload that is sent to the `Bot.on_button_chat_create` decorator.

        :param timestamp: Timestamp of the button press
        :param chat: Created chat
        :param message_id: Message ID on which the button was
        :param start_payload: Start payload specified by the button
        '''
        self.timestamp: int = timestamp
        self.chat: Chat = chat
        self.message_id: "str | None" = message_id
        self.start_payload: "str | None" = start_payload


    @staticmethod
    def from_json(data: dict) -> "ChatCreatePayload | None":
        if data == None: return None
        
        return ChatCreatePayload(
            data['timestamp'],
            Chat.from_json(data['chat']),
            data.get('message_id', None),
            data.get('start_payload', None)
        )
    


class MessageDeletePayload:
    def __init__(self,
        timestamp: int,
        message: "Message | None" = None,
        message_id: "str | None" = None,
        chat_id: "int | None" = None,
        user_id: "int | None" = None
    ):
        '''
        Payload that is sent to the `Bot.on_message_delete` decorator.

        :param timestamp: Timestamp of the message deletion.
        :param message: Cached Message object. May be None if message was not cached
        :param message_id: ID of the deleted message
        :param chat_id: ID of the chat the message was deleted in
        :param user_id: ID of the user who deleted the message
        '''
        self.timestamp: int = timestamp
        self.message: "Message | None" = message
        self.message_id: "str | None" = message_id
        self.chat_id: "int | None" = chat_id
        self.user_id: "int | None" = user_id


    @staticmethod
    def from_json(data: dict, bot) -> "MessageDeletePayload | None":
        if data == None: return None
        
        return MessageDeletePayload(
            data['timestamp'],
            bot.cache.get_message(data.get('message_id', None)),
            data.get('message_id', None),
            data.get('chat_id', None),
            data.get('user_id', None),
        )


    @property
    def content(self) -> "str | None":
        if self.message == None:
            return None
        
        return self.message.content
    

class ChatTitleEditPayload:
    def __init__(self,
        timestamp: int,
        user: User,
        chat_id: "int | None" = None,
        title: "str | None" = None
    ):
        '''
        Payload that is sent to the `Bot.on_chat_title_change` decorator.

        :param timestamp: Timestamp of the title edit.
        :param user: User that edited the chat name.
        :param chat_id: Chat ID that had its title edited.
        :param title: New chat title
        '''
        self.timestamp: int = timestamp
        self.user: User = user
        self.chat_id: "int | None" = chat_id
        self.title: "str | None" = title


    @staticmethod
    def from_json(data: dict) -> "ChatTitleEditPayload | None":
        if data == None: return None
        
        return ChatTitleEditPayload(
            data['timestamp'],
            User.from_json(data['user']),
            data.get('chat_id', None),
            data.get('title', None),
        )


class ChatMembershipPayload:
    def __init__(self,
        timestamp: int,
        user: User,
        chat_id: "int | None" = None,
        is_channel: bool = False
    ):
        '''
        Payload that is sent to the `Bot.on_bot_add` or `Bot.on_bot_remove` decorator.

        :param timestamp: Timestamp of the action.
        :param user: User that invited or kicked the bot.
        :param chat_id: Chat ID that the bot was invited to / kicked from.
        :param is_channel: Whether the bot got added to / kicked from a channel or not
        '''
        self.timestamp: int = timestamp
        self.user: User = user
        self.chat_id: "int | None" = chat_id
        self.is_channel: bool = is_channel


    @staticmethod
    def from_json(data: dict) -> "ChatMembershipPayload | None":
        if data == None: return None
        
        return ChatMembershipPayload(
            data['timestamp'],
            User.from_json(data['user']),
            data.get('chat_id', None),
            data.get('is_channel', False),
        )


class UserMembershipPayload:
    def __init__(self,
        timestamp: int,
        user: User,
        chat_id: "int | None" = None,
        is_channel: bool = False,
        initiator: "int | None" = None
    ):
        '''
        Payload that is sent to the `Bot.on_user_add` or `Bot.on_user_remove` decorator.

        :param timestamp: Timestamp of the action.
        :param user: User that joined or left the chat.
        :param chat_id: Chat ID that the user joined / left.
        :param is_channel: Whether the user was added to / kicked from a channel or not.
        :param initiator: User ID of the inviter / kicker, if the user got invited by another user or kicked by an admin.
        '''
        self.timestamp: int = timestamp
        self.user: User = user
        self.chat_id: "int | None" = chat_id
        self.is_channel: bool = is_channel
        self.initiator: "int | None" = initiator


    @staticmethod
    def from_json(data: dict) -> "UserMembershipPayload | None":
        if data == None: return None
        
        return UserMembershipPayload(
            data['timestamp'],
            User.from_json(data['user']),
            data.get('chat_id', None),
            data.get('is_channel', False),
            data.get('inviter_id', data.get('admin_id', None))
        )
