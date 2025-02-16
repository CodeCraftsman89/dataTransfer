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