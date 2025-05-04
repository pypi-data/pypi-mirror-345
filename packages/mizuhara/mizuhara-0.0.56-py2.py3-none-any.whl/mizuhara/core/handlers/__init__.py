from datetime import datetime
from telebot.types import (Message,
                           CallbackQuery,
                           ForceReply,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton,)
from execute import bot


class Receiver:
    """
    Receiver:
    This class will give message itself or message with callback query, responding to telegram user's request.

    :param types: message or callback. Types should be assigned during creating instance of handler class in project/views.py

    * types: assigned message or callback query
    * request_user: information of telegram user who sent a message or callback data
    * chat_id: the ID of chat between bot and telegram user
    * callback_id: callback id (if types is callback query)
    * message_id: message id (if types is message)
    * timestamp: timestamp when the message or callback query comes in.
    * rcv_datetime: ISO datetime for timestamp
    * client_response: content of callback data or message that telegram user sent to bot.

    This class is created for template. It is recommended not to user this class directly.
    """

    def __init__(self, types):
        self.types = types
        self.bot = bot
        self.request_user = self.types.from_user
        self.chat_id = self.types.from_user.id
        self.callback_id: int = None if type(self.types) == Message else self.types.id
        self.message_id: int = self.types.id if type(self.types) == Message else self.types.message.id
        self.timestamp: int = self.types.date if type(self.types) == Message else datetime.timestamp(datetime.now())
        self.rcv_datetime: datetime = datetime.fromtimestamp(self.timestamp)
        self.client_response = self.types.text if type(self.types) == Message else self.types.data

    async def send_message(self):
        pass
