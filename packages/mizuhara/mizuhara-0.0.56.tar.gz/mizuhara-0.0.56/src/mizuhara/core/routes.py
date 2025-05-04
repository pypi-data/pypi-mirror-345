from execute import bot
from config import ALLOWED_CHAT_TYPE
from . import UserInfo


# temporarily save the client information
CLIENT_INFO: dict = {}


def connector_callback(view,
                       callback_data:str|list|tuple|None=None,
                       allowed_pre_route:str|list|tuple|None=None,
                       **kwargs) -> None:
    """
    connector_callback:
    mapper function between route and callback view.

    :param view: function class that you want to map with specific route
    :param allowed_pre_route: route that the client can access.
    :param callback_data: set the callback data in list to response with InlineKeyboardButton
    :param kwargs:
    :return:
    """

    bot.callback_query_handler(func=lambda callback: route_process(types=callback,
                                                                   allowed_pre_route=allowed_pre_route,
                                                                   callback_data=callback_data,),
                               **kwargs)(view)
    return None


def connector_command(view,
                      commands:str|list|tuple="start",
                      allowed_pre_route:str|list|tuple|None=None,
                      **kwargs) -> None:
    """
    connector_command:
    mapper function between route and command view.

    :param view:
    :param commands:
    :param allowed_pre_route:
    :param kwargs:
    :return:
    """

    bot.message_handler(commands=commands.replace(" ", "").split(",") if isinstance(commands, str) else commands,
                        func=lambda message: route_process(types=message,
                                                           allowed_pre_route=allowed_pre_route),
                        chat_types=ALLOWED_CHAT_TYPE,
                        **kwargs)(view)
    return None


def connector_message(view,
                      allowed_pre_route:str|list|tuple|None=None,
                      **kwargs) -> None:
    """
    connector_message:
    mapper function between route and message view.

    :param view:
    :param allowed_pre_route:
    :param kwargs:
    :return: None
    """

    bot.message_handler(func=lambda message: route_process(types=message,
                                                           allowed_pre_route=allowed_pre_route,
                                                           reset_index=False),
                        chat_types=ALLOWED_CHAT_TYPE,
                        **kwargs)(view)
    return None


def __check_client_info(chat_id:int, reset_index:bool, types) -> dict:
    """
    __check_client_info:
    this method is charge of checking and assigning client info for first access.
    Client needs client information dictionary before using telegram bot.

    :param chat_id: get from route_process.
    :param reset_index: set bool whether reset index or not.
    :param types: types from client requests
    :return: None
    """

    if CLIENT_INFO.get(chat_id, None) is None:
        CLIENT_INFO.update({chat_id: UserInfo(types=types)})

    else:
        if reset_index:
            CLIENT_INFO[chat_id].update(data={}, index=0)

    return CLIENT_INFO[chat_id]


def __check_callback(reply, callback_data:str|list|tuple|None) -> bool:
    """
    __check_callback:
    this method is charge of checking callback data during callback processes.
    this class is not designed for direct use.

    :param reply: get from route_process (message or callback)
    :param callback_data: get from route_process
    :return: bool
    """

    if isinstance(callback_data, str):
        callback_data = callback_data.replace(" ", "").split(",")

    if getattr(reply, "data", None):
        if reply.data.endswith(("__>", "__<")):
            reply_data = reply.data.split("__")
            data = reply_data[0]
            symbol = reply_data[1]
            if callback_data is not None and data in callback_data:
                page = CLIENT_INFO[reply.from_user.id].get("page")
                if symbol == ">":
                    CLIENT_INFO[reply.from_user.id].update(page=page + 1)

                elif symbol == "<":
                    CLIENT_INFO[reply.from_user.id].update(page=page - 1)

            return data in callback_data if callback_data is not None else True

        CLIENT_INFO[reply.from_user.id].update(page=0)

    return reply.data in callback_data if callback_data is not None else True


def __check_route(client_info:dict, allowed_pre_route:str|list|tuple|None) -> bool:
    """
    __check_route:
    this method is charge of checking allowed route during executing telebot processes.
    this class is not designed for direct use.

    :param client_info: get from route_process
    :param allowed_pre_route: get from route_process
    :return: bool
    """

    client_route: str | None = client_info.get("route", None) if client_info is not None else None
    if isinstance(allowed_pre_route, str):
        allowed_pre_route = allowed_pre_route.replace(" ", "").split(",")

    return client_route in allowed_pre_route if allowed_pre_route is not None else True


def route_process(types,
                  allowed_pre_route:str|list|tuple|None=None,
                  callback_data:str|list|tuple|None=None,
                  reset_index:bool=True) -> bool:
    """
    route_process:
    route_process is related with validating callback data or route and assigning route for telebot processes.
    this function is return bool so that acts as a condition in handlers.

    please refer to:
    https://pytba.readthedocs.io/en/latest/sync_version/index.html#telebot.TeleBot.message_handler

    :param types: message or callback
    :param allowed_pre_route:
    :param callback_data:
    :param reset_index:
    :return:
    """

    chat_id: int = types.from_user.id
    client_info: dict | None = __check_client_info(chat_id=chat_id, reset_index=reset_index, types=types)
    condition1: bool = __check_route(client_info=client_info, allowed_pre_route=allowed_pre_route)
    condition2: bool = __check_callback(reply=types, callback_data=callback_data)
    return True if condition1 and condition2 else False
