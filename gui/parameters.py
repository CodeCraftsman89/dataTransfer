class Message:
    _types_messages = ["connected", "send_all", "send", "disconnect"]

    def __init__(self, type_msg: str, nick_from: str, nick_to: str = None, message: str = None):
        self.type_msg = type_msg
        self.nick_from = nick_from
        self.nick_to = nick_to
        self.message = message

    @staticmethod
    def basic_types():
        return Message._types_messages

class ChatKeys:
    btn = "button"
    nick = "client_nick"
    msg_text = "messanger_text"

class Base:
    window_title = "YellowGram"
    name_for_chat_all = "All"
    window_width = 1000
    window_height = 700
    check_connection_pause = 5000
    receiver_event = "<<receive>>"

class Connection:
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 35533
    NICK = "|fweffIOK"
    SEP_HEAD = b'/x00'
    SEP_FIELDS = b'/x01'
    CONNECT = "CONN_NICK"
    GET_ALL = "GET_NICKS"
    SEND_NICK = "SEND"
    SEND_ALL_NICKS = "SEND_ALL"
    DISCONNECT = "DISCONN"

class Colors:
    bg_window_color = "khaki2"
    chat_messanger_bg_color = 'gold2'
    send_messages_bg_color = 'gold3'

    btn_text_color = 'OrangeRed4'
    btn_send_color = 'SandyBrown'

    button_list_color = bg_window_color
    btn_chat_color = bg_window_color
    btn_chat_text_color = 'DarkOrange'

    message_from_user_bg_color = 'light goldenrod'
    message_from_user_text_color = 'tomato'

    message_from_other_bg_color = 'sienna4'
    message_from_other_text_color = 'firebrick4'

class FontBtnChat:
    family = "TimesNewRoman"
    size = 20
    weight = 'bold'
    slant = 'roman'

class FontMsgUser:
    family = 'TiemsNewRoman'
    size = 14
    slant = 'italic'

class FontMsgOther:
    family = "TimesNewRoman"
    size = 14
    slant = 'roman'