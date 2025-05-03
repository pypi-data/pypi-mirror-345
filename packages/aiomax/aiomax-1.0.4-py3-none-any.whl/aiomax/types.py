class Actions:
    TYPING_ON = "typing_on"
    SENDING_PHOTO = "sending_photo"
    SENDING_AUDIO = "sending_audio"
    SENDING_FILE = "sending_file"
    MARK_SEEN = "mark_seen"

class ChatType:
    DIALOG = "dialog"
    CHAT = "chat"
    CHANNEL = "channel"

class MessageLinkType:
    FORWARD = "forward"
    REPLY = "reply"

class ChatAdminPermission:
    READ_ALL_MESSAGES = "read_all_messages"
    ADD_REMOVE_MEMBERS = "add_remove_members"
    CHANGE_CHAT_INFO = "change_chat_info"
    PIN_MESSAGE = "pin_message"
    WRITE = "write"

class ChatStatus:
    ACTIVE = "active"
    REMOVED = "removed"
    LEFT = "left"
    CLOSED = "closed"
    SUSPENDED = "suspended"

class ButtonType:
    CALLBACK = "callback"
    LINK = "link"
    REQUEST_GEO_LOCATION = "request_geo_location"
    REQUEST_CONTACT = "request_contact"
    CHAT = "chat"