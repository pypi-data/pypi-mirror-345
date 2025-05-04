import sys
from os import mkdir, listdir


ROUTES_TEXT: str = \
"""from mizuhara.core.routes import (connector_callback,
                                  connector_command,
                                  connector_message,)


# Mapping handlers and views for Telegram Bot commands.
COMMANDS: list = [
]


MESSAGES: list = [
]


CALLBACKS: list = [
]

"""

SERIALIZERS_TEXT: str = \
"""# please import handlers classes in core.handlers
# and inherit one of them to your custom handler serializer classes.
from mizuhara.core.handlers.handlers import *
from mizuhara.core.routes import CLIENT_INFO


# please write down your code below.

"""

VIEWS_TEXT: str = \
"""from execute import bot
# do not edit above this line.
# please write down your code below.

"""

EXECUTE_TEXT: str = \
"""import asyncio
from importlib import import_module
from telebot.async_telebot import (logger,
                                   AsyncTeleBot,)
from config import *


# create a Telegram Bot instance
bot = AsyncTeleBot(token=TELEBOT_TOKEN,
                   parse_mode=PARSE_MODE,
                   offset=OFFSET,
                   exception_handler=EXCEPTION_HANDLER,
                   state_storage=STATE_STORAGE,
                   disable_web_page_preview=DISABLE_WEB_PAGE_PREVIEW,
                   disable_notification=DISABLE_NOTIFICATION,
                   protect_content=PROTECT_CONTENT,
                   allow_sending_without_reply=ALLOW_SENDING_WITHOUT_REPLY,
                   colorful_logs=COLORFUL_LOG,
                   validate_token=VALIDATE_TOKEN)


# ignore unnecessary warning log
warning_filter = logging.Filter()
warning_filter.filter = lambda x: not ("deprecated" in x.getMessage().lower() and x.levelno == logging.WARNING)

# set Log Level
logger.setLevel(level=logging.ERROR)
logger.addFilter(filter=warning_filter)

mizuhara_logger = logging.getLogger("Mizuhara")
mizuhara_logger.setLevel(level=LOG_LEVEL)
mizuhara_logger.handlers = logger.handlers


# main for set menu and polling.
async def execute() -> None:
    await bot.set_my_commands(commands=MENU_COMMANDS)
    await bot.polling()
    return None


# start main
if __name__ == "__main__":
    # import handlers in installed app.
    for app_name in INSTALLED_APPS:
        try:
            module = import_module(f"{app_name}.routes")
            names_to_import = [name for name in dir(module) if not name.startswith("_")]
            for name in names_to_import:
                globals()[name] = getattr(module, name)

        except (ImportError, AttributeError) as e:
            if isinstance(e, ImportError):
                logger.error(f"Improper App Name '{app_name}': {e}")

            else:
                logger.error(f"accessing attributes in module {app_name}: {e}")

            break

    # execute polling in asynchronous
    asyncio.run(execute())
"""

CONFIG_TEXT: str = \
"""# Set the argument for asynchronous telebot instance.

from os import getenv
from telebot.types import BotCommand


### TELEGRAM BOT CONFIG ###
# Set the Telegram Bot API TOKEN for Telegram Bot Father
# User must set this value before executing main.py
# it is recommended to export the value for environment variables.
# - sh: export TELEBOT_TOKEN=YOUR_BOT_TOKEN
TELEBOT_TOKEN: str = getenv("TELEBOT_TOKEN")


# Set the parse mode for Telegram Bot.
# default is None.
# possible values: "HTML", "Markdown"
PARSE_MODE: str | None = None


# Set the offset for Telegram Bot.
# default is None.
# possible value: positive int
# process the requests of message after specific ID' message
OFFSET: int | None = None


# Set the exception for Telegram Bot.
# import custom exception handler and assign it to EXCEPTION_HANDLER.
# default is handlers.exception_handlers.custom_exception_handler
EXCEPTION_HANDLER = None


# Set the way to store and maintain the status of Telegram Bot.
# bot will read the last status of telegram bot from file, DB or memory during restart process.
# default is None and it will store the status information in memory.
# possible values: class in telebot.storage package
# - StateMemoryStorage, StateStorageBase(use class inheriting this class), StateRedisStorage
STATE_STORAGE = None


# Set the web_page_preview config.
# it will show a preview of a linked web page(protocol://host.domain) in message or not
# default is None(False)
DISABLE_WEB_PAGE_PREVIEW: bool | None = False


# Set the notification for bot message(alarm or vibration on your phone).
# default is None(False) - will give you alarm or vibration.
DISABLE_NOTIFICATION: bool | None = False


# Set the message protection
# preventing users from copying and forwarding sent bot message.
# default is None(False)
PROTECT_CONTENT: bool | None = True


# Set the bot's action about sending message to user.
# bot can only send standalone message after user's request if the value is set for False
# default is None(True)
ALLOW_SENDING_WITHOUT_REPLY: bool | None = False


# Set the colorful log config
# require 'coloredlogs' package in pip before using it.
# default is None(False)
COLORFUL_LOG: bool | None = True


# Set whether the bot validates its token or not.
# default is True
VALIDATE_TOKEN: bool | None = True


# Import handlers
INSTALLED_APPS: list | tuple = (
)

### TELEGRAM BOT CONFIG END ###

### TELEGRAM BOT FRAMEWORK CONFIG ###
# Set the allowed chat_type.
# default is ["private"]
# possible values: "private", "group", "supergroup", "channel"
ALLOWED_CHAT_TYPE: list = ["private"]


# Set menu button for your bot.
# use BotCommand(command="YOUR_COMMAND", description="COMMAND_DESCRIPTION")
# command name should be lower cases.
# if you change MENU_COMMANDS, remove your bot and re-enter to apply changes.
MENU_COMMANDS: list = [
    BotCommand(command="main", description="Main"),
]

# Set chatting mode for your bot.
# SECRET_MODE is a bool variable that decides whether the previous messages will be removed or not.
# if True, bot will remove all remained messages in chat room after user types messages or click InlineMarkupButton
SECRET_MODE: bool = True

### TELEGRAM BOT FRAMEWORK CONFIG END###

### LOGGING CONFIG ###
# Set the log level
# default is INFO
# possible values: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
LOG_LEVEL = "INFO"


### LOGGING CONFIG END ###

"""


def main():
    """
    code for CLI command that create a telebot_framework project.

    :return: None
    """

    argv = sys.argv[1:]

    try:
        subcommand = argv[0]
        if subcommand == "newproject":
            create_project()

        elif subcommand == "newapp":
            create_app(name=argv[1])

        return None

    except IndexError as e:
        pass

    print_help()
    return None


def create_project():
    # create file: config.py
    with open("./config.py", mode="w", encoding="utf-8") as f:
        f.write(CONFIG_TEXT)

    # create file: execute.py
    with open("./execute.py", mode="w", encoding="utf-8") as f:
        f.write(EXECUTE_TEXT)

    # create translate yml files.
    mkdir(path="./translation")
    with open("./translation/buttons.yml", mode="w") as f:
        f.write("")

    with open("./translation/exceptions.yml", mode="w") as f:
        f.write("")

    with open("./translation/exceptions.yml", mode="w") as f:
        f.write("")

    with open("./translation/handlers.yml", mode="w") as f:
        f.write("")

    with open("./translation/warnings.yml", mode="w") as f:
        f.write("")

    return None

def create_app(name:str):
    # check the project initiation
    if ("config.py" and "execute.py") not in listdir():
        create_project()

    mkdir(f"./{name}")

    # create file: __init__.py
    with open(f"./{name}/__init__.py", mode="w", encoding="utf-8") as f:
        f.write("")

    # create file: routes.py
    with open(f"./{name}/routes.py", mode="w", encoding="utf-8") as f:
        f.write(ROUTES_TEXT)

    with open(f"./{name}/serializers.py", mode="w", encoding="utf-8") as f:
        f.write(SERIALIZERS_TEXT)

    with open(f"./{name}/views.py", mode="w", encoding="utf-8") as f:
        f.write(VIEWS_TEXT.format(name))

    return None


def print_help():
    """
    code for printing out usage of command 'mizuhara'

    :return: None
    """

    print("Help Message")
    pass
