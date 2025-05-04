import re
from os import makedirs
from shutil import rmtree
from telebot.util import quick_markup
from telebot.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup,
                           ForceReply)
from telebot.asyncio_helper import ApiTelegramException
from mizuhara.core.handlers import (Receiver,
                           CallbackQuery)
from mizuhara.core.routes import CLIENT_INFO, UserInfo
from mizuhara.translation import translate
from mizuhara.config import SECRET_MODE
from execute import mizuhara_logger


class ReceiverBasic(Receiver):
    """
    ReceiverBasic:
    This class will give message, responding to telegram user's request.
    This class inherits Receiver class.

    :param types: message or callback. Types should be assigned during creating instance of handler class in project/views.py
    :kwargs:
      - bot_text: content text contained in message that the bot will send to telegram user. Default is None
      - bot_markup: markup contained in message that the bot will send to telegram user. Default is None.
      - remove_user_msg: bool value to decide to remove previous all user messages in chat room. Default is False(not remove)
      - route: set the telegram user's route in your bot application.

    Use this class when you need to get a telegram user's request and just send a simple message with overriding send_message()
    """

    def __init__(self, types, **kwargs):
        super(ReceiverBasic, self).__init__(types=types)
        self.bot_text: str | None = kwargs.get("bot_text", None)
        self.bot_markup = kwargs.get("bot_markup", None)
        self.remove_user_msg = kwargs.get("remove_prev_msg", False)
        self.route = kwargs.get("route", None)

        if CLIENT_INFO.get(self.chat_id) is None:
            CLIENT_INFO[self.chat_id] = UserInfo(types=self.types)

        if self.route is not None:
            CLIENT_INFO[self.chat_id].update(route=self.route)

        self._logging_init()

    def _logging_init(self) -> None:
        """
        _logging_init:
        this method leave the info level log after creating the class instance.

        :return: None
        """
        log: str = f"chat_id: {self.chat_id}, msg_id: {self.message_id}, is_bot: {self.request_user.is_bot}, route: {self.route}"
        mizuhara_logger.info(log)
        return None

    async def _remove_prev_message(self) -> bool:
        """
        _remove_prev_message:
        This method decides whether it remove previous messages including InlineMarkup after user selection.

        if self.remove == True: remove all bots messages and user messages.
        else:                   remove all user messages(with text) only.

        :return: bool
        """

        if type(self.types) == CallbackQuery:
            # send user's selection to telegram bot.
            await self.bot.answer_callback_query(callback_query_id=self.callback_id)

            # if self.bot_text is None, remove previous buttons and pop up new Button on where previous button existed.
            if self.bot_text is None:
                await self.bot.edit_message_reply_markup(chat_id=self.chat_id,
                                                         message_id=self.message_id,
                                                         reply_markup=self.bot_markup or InlineKeyboardMarkup())
                return False

        await self.__remove_messages()
        return True

    async def __remove_messages(self) -> None:
        """
        __remove_messages:
        this method is charge of only removing previous 3 messages left on chat room.

        :return:
        """
        try:
            # remove previous bot message if SECRET_MODE is True
            if SECRET_MODE:
                for num in range(10):
                    await self.bot.delete_message(chat_id=self.chat_id, message_id=self.message_id - num)

            else:
                if self.remove_user_msg:
                    await self.bot.delete_message(chat_id=self.chat_id, message_id=self.message_id)

        except ApiTelegramException:
            pass

        return None

    async def send_message(self) -> None:
        """
        send_message:
        this method will make bot send message with bot_text to telegram user.
        or use as a forking point with if-else condition by overriding this method.

        :return: None
        """

        if await self._remove_prev_message():
            await self.bot.send_message(chat_id=self.chat_id,
                                        text=self.bot_text,
                                        reply_markup=self.bot_markup)
        return None


class ReceiverWithForceReply(ReceiverBasic):
    """
    ReceiverWithForceReply:
    This class will give ForceReply markup message, responding to telegram user's request.
    This class inherits ReceiverBasic class.

    Use this class when you need to get several user's input consecutively. for example,
    - 'Sign in' requires username and password from user.
    - 'Sign Up' requires username, password, first_name and last_name
    """

    class Meta:
        """
        This class is an inner Meta class for ReceiverWithForceReply.

        * fields: fields name that the user must input.
        * fields_text: fields text to guide telegram user.
        * fields_regex: fields regex that telegram user must input in a specific field.
        * fields_error_msg: error text to inform telegram user of regex mismatch.
        """

        fields: list | tuple | None = None
        fields_text: str | list | tuple | None = None
        fields_regex: str | list | tuple | None = None
        fields_error_msg: str | list | tuple | None = None

    def __init__(self, types, link_route, **kwargs):
        super(ReceiverWithForceReply, self).__init__(types=types, **kwargs)
        self.client_data = CLIENT_INFO[self.chat_id].get("data")
        self.link_route = link_route

        self.fields = getattr(self.Meta, 'fields', ())
        if not isinstance(self.fields, (tuple, list)):
            raise ValueError(translate(domain="exceptions", key="err_force_reply_fields_type", types=self.types))

        if len(self.fields) == 0:
            raise AttributeError(translate(domain="exceptions", key="err_force_reply_empty_field", types=self.types))

        self.fields_text = self._translate_fields_text()
        self.fields_regex = getattr(self.Meta, 'fields_regex', {field: ".*" for field in self.fields})
        self.fields_error_msg = self._translate_fields_error_msg()

    def _logging_init(self) -> None:
        index: int = CLIENT_INFO[self.chat_id].get("index")

        try:
            log_info: str = f"chat_id: {self.chat_id}, msg_id: {self.message_id}, is_bot: {self.request_user.is_bot}, field: {self.Meta.fields[index]}, index: {index + 1}/{len(self.Meta.fields)}"

        except IndexError:
            log_info: str = f"chat_id: {self.chat_id}, msg_id: {self.message_id}, is_bot: {self.request_user.is_bot}, action: send_data"

        mizuhara_logger.info(log_info)
        return None

    def _translate_fields_text(self) -> dict:
        if getattr(self.Meta, "fields_text", None) is None:
            return {field: translate(domain="handlers", key=field, types=self.types)
                    for field in self.fields}

        return {k: translate(domain="handlers", key=v, types=self.types)
                for k, v in self.Meta.fields_text.items()}

    def _translate_fields_error_msg(self) -> dict:
        if getattr(self.Meta, 'fields_error_msg', None) is None:
            return {field: translate(domain="warnings",
                                     key="warn_regex_mismatch",
                                     types=self.types).format(field)
                    for field in self.fields}

        tmp = {}
        for k, v in self.Meta.fields_error_msg.items():
            if type(v) in [list, tuple]:
                tmp.update({k: [translate(domain="warnings", key=atom, types=self.types)
                                for atom in v]})

            else:
                tmp.update({k: translate(domain="warnings", key=v, types=self.types)})

        return tmp

    async def get_client_data(self) -> bool:
        """
        get_client_data:

        This method gets severer inputs from telegram user, referring to the Meta.field.
        -  send message to telegram user to guide what text user must input.
        -  get user input for each field
        -  check the regex with user input.
        -  save relative data in "data" in CLIENT_INFO

        :return: bool
        """

        flag = False
        index: int = CLIENT_INFO[self.chat_id].get("index")

        # Receiving User Input.
        # Condition ignore index 0 because index 0 is a callback.data, not a message.text
        if index != 0 :
            pre_index = index - 1
            pre_field = self.fields[pre_index]
            regex_list = self.fields_regex.get(pre_field, [".*"])
            error_msg = self.fields_error_msg.get(pre_field,
                                                  translate(domain="warnings",
                                                            key="warn_input_regex_mismatch",
                                                            types=self.types).format(pre_field))

            if not isinstance(regex_list, (list, tuple)):
                regex_list = [regex_list]

            if not isinstance(error_msg, (list, tuple)):
                error_msg = [error_msg]

            # check regex with telegram user's input.
            for regex in regex_list:
                inner_index = regex_list.index(regex)
                if not re.search(pattern=regex, string=self.client_response):
                    self.bot_text = error_msg[0] if len(error_msg) != len(regex_list) else error_msg[inner_index]
                    self.bot_markup = None
                    CLIENT_INFO[self.chat_id].update(index=0)
                    flag = True
                    break

            # if regex is not match.
            if flag:
                await self.send_message()
                CLIENT_INFO[self.chat_id].update(index=index - 1)
                index -= 1
                self.bot_markup = ForceReply()
                flag = False

            else:
                # save user's input to CLIENT_INFO, especially in "data"
                CLIENT_INFO[self.chat_id].data.update({pre_field: self.client_response})

        # Index is not equal to length of fields in Meta class.
        if index != len(self.fields):
            field = self.fields[index]

            # provide cancel button.
            self.bot_text = translate(domain="handlers",
                                      key="guide_force_reply_cancel",
                                      types=self.types)
            self.bot_markup = quick_markup(values={})
            self.bot_markup.add(InlineKeyboardButton(text=translate(domain="buttons",
                                                                    key="cancel",
                                                                    types=self.types),
                                                     callback_data=self.link_route))
            await self.bot.send_message(chat_id=self.chat_id,
                                        text=self.bot_text,
                                        reply_markup=self.bot_markup)

            self.bot_text = self.fields_text[field]
            self.bot_markup = ForceReply()

            # update index number for referring.
            CLIENT_INFO[self.chat_id].update(index=index + 1)

        # if user gave input for last field,
        else:
            index: int = CLIENT_INFO[self.chat_id].get("index") - 1

            # save user's last input to CLIENT_INFO[self.chat_id]["data"]
            CLIENT_INFO[self.chat_id].data.update({self.fields[index]: self.client_response})

            # process with user data. it must be overridden by developer.
            await self.post_process()

            # reset CLIENT_INFO and bot_markup.
            CLIENT_INFO[self.chat_id].update(index=0, data={})
            self.bot_markup = None
            flag = True

        if self.bot_text is not None:
            await self.send_message()
        return flag

    async def post_process(self):
        """
        post_process:
        This method is charge of processing user input saved in CLIENT_INFO[self.chat_id]["data"]
        Developer must override this method for post job. for example: API Calling

        :return:
        """

        pass

    async def send_message(self) -> None:
        """
        send_message:
        This method will make bot send message to telegram user.
        It can remove user message before sending bot message to telegram user.

        :return: None
        """

        await super().send_message()
        return None


class ReceiverWithInlineMarkup(ReceiverBasic):
    """
    ReceiverWithInlineMarkup:
    This class will give message with InlineMarkupButton, responding to telegram user's request.
    This class inherits ReceiverBasic class.

    Use this class if you need to send several InlineMarkupButtons to telegram user.
    """

    class Meta:
        """
        This class is an inner Meta class for ReceiverWithForceReply.

        * fields: InlineMarkupButton text that show to telegram user.
        * fields_callback: callback data behind each InlineMarkupButton
        * fields_url: url string behind each InlineMarkupButton.
        """

        fields = None
        fields_callback = None
        fields_url = None

    def __init__(self, types, **kwargs):
        super(ReceiverWithInlineMarkup, self).__init__(types=types, **kwargs)
        self.fields: list|tuple = getattr(self.Meta, 'fields', ())
        self.row_width: int = kwargs.get("row_width", 2)

        if self.fields is not None:
            self.fields_callback = getattr(self.Meta, "fields_callback", {field: field.lower().replace(" ", "_") for field in self.fields})
            self.fields_url = getattr(self.Meta, "fields_url", {field: None for field in self.fields})
            self.values = {translate(domain="buttons",
                                     key=key,
                                     types=self.types): {
                "callback_data": self.fields_callback.get(key, key.lower().replace(" ", "_")),
                "url": self.fields_url.get(key, None),
            } for key in self.fields}
            self.bot_markup = quick_markup(values=self.values, row_width=self.row_width)

    async def get_client_data(self) -> any:
        """
        get_client_data:
        This method is responsible to send message with InlineMarkupButton.

        :return: any
        """

        await self.pre_process()
        await super().send_message()
        return await self.post_process()

    async def post_process(self):
        """
        post_process:
        This method is charge of processing user input saved in CLIENT_INFO[self.chat_id]["data"]
        Developer must override this method for post job. for example: API Calling

        :return:
        """

        pass

    async def pre_process(self) -> None:
        """
        pre_process
        This class is charge of setting self.bot_text to print out text information.

        Please set self.bot_text by overriding this method.

        :return: None
        """

        pass


class ResultShowingWithInlineMarkup(ReceiverWithInlineMarkup):
    """
    ResultShowingWithInlineMarkup:

    If you want to show some result to telegram user and user have to check before doing next process,
    this class will provide 'Continue' button on the chat room.
    """

    class Meta:
        fields = ["Continue"]
        fields_callback: dict = {
            "Continue": None
        }

    def __init__(self, types, link_route: str, **kwargs):
        self.Meta.fields_callback.update({self.Meta.fields[0]: link_route})
        super(ResultShowingWithInlineMarkup, self).__init__(types, **kwargs)

    async def send_message(self) -> None:
        """
        send_message:
        send_message with result that comes from the last process in method self.pre_process().

        :return: None
        """

        await self.pre_process()
        await super().send_message()
        return None


class ReceiverWithInlineMarkupPagination(ReceiverWithInlineMarkup):
    """
    ReceiverWithInlineMarkupPagination:

    If you want to create a plenty of InlineKeyboard Buttons and need pagination, use this class.
    this class will provide page moving button at the below of buttons.

    * basic route: set the route after clicking '<' or '>' button.
    * parent_route: set the route after clicking 'Cancel' button.
    * num_in_page: set the number of buttons in one page.

    """

    def __init__(self, types, basic_route:str, parent_route:str, num_in_page:int=6, **kwargs):
        super(ReceiverWithInlineMarkupPagination, self).__init__(types, **kwargs)

        self.page = CLIENT_INFO[self.chat_id].get("page")
        self.num_in_page = num_in_page
        start_idx = self.page * self.num_in_page
        end_idx = start_idx + self.num_in_page
        total_page = int(len(self.fields) / self.num_in_page)

        key_list = list(self.values.keys())[start_idx:end_idx]
        self.values = {k:self.values[k] for k in key_list}
        self.bot_markup = quick_markup(values=self.values, row_width=self.row_width)

        # Additional Buttons.
        self.bot_markup.add(InlineKeyboardButton(text=translate(domain="buttons",
                                                                key="cancel",
                                                                types=self.types),
                                                 callback_data=f"{parent_route}"))
        if total_page != 0:
            if 0 < self.page < total_page:
                self.bot_markup.add(InlineKeyboardButton(text="<", callback_data=f"{basic_route}__<"),
                                    InlineKeyboardButton(text=">", callback_data=f"{basic_route}__>"))

            elif self.page == total_page:
                self.bot_markup.add(InlineKeyboardButton(text="<", callback_data=f"{basic_route}__<"))

            elif self.page == 0 and len(self.fields) != len(key_list):
                self.bot_markup.add(InlineKeyboardButton(text=">", callback_data=f"{basic_route}__>"))

    def _logging_init(self) -> None:
        log: str = f"chat_id: {self.chat_id}, msg_id: {self.message_id}, is_bot: {self.request_user.is_bot}, route: {self.route}, page: {CLIENT_INFO[self.chat_id].get("page") + 1}"
        mizuhara_logger.info(log)
        return None


class SenderWithBasic(ResultShowingWithInlineMarkup):
    """
    SenderWithBasic:

    this class is charge of sending message only with attachment(file, image or something)
    this class is a template so do not use it directly.

    the bot will send created image to telegram user.
    """

    FILE_STORAGE_FOLDER: str = "core/tmp_storage"

    def __init__(self, types, filename:str, **kwargs):
        super(SenderWithBasic, self).__init__(types=types, **kwargs)
        self.filename = filename
        self.filepath = f"{SenderWithBasic.FILE_STORAGE_FOLDER}/{self.chat_id}/{filename}"
        self.content = None
        self.bot_text = self.bot_text if self.bot_text is not None \
            else translate(domain="handlers", key="sender_with_basic_download", types=self.types)

    async def _send_message(self):
        """
        this class is an inner method in send_message() which is important to send image or docs contents.
        each Sender__ class must override this method to send contents with text message.

        :return: None
        """
        pass

    async def __create_file(self, content) -> None:
        """
        this method is charge of producing new image with content from pre_process.

        :param content: content that you would like to write in a file.
        :return: None
        """

        mode: str = "wb" if isinstance(self.content, bytes) else "w"
        content = content if isinstance(self.content, bytes) else str(content)
        while True:
            try:
                with open(self.filepath, mode=mode) as file:
                    file.write(content)
                    break

            except FileNotFoundError:
                makedirs(name="/".join(self.filepath.split("/")[:-1]), exist_ok=True)

        return None

    async def __remove_file(self):
        """
        this method removes download file which was temporarily stored in FILE_STORAGE_FOLDER.

        :return: None
        """

        rmtree("/".join(self.filepath.split("/")[:-1]))
        return None

    async def pre_process(self) -> None:
        """
        create a content that you want to write down on download file by overriding this method.
        set your content by saving on self.content

        :return: None
        """

        return None

    async def send_message(self) -> None:
        """
        this method is charge of sending message with attachment.

        :return: None
        """
        # Save content to the filepath.
        await self.pre_process()

        # exit if there is no content
        if self.content is None:
            self.bot_text = translate(domain="warnings",
                                      key="warn_doc_without_content",
                                      types=self.types)
            await super().send_message()
            return None

        # create a file with received content
        await self.__create_file(content=self.content)

        # send message, if there is a self.bot_text
        if await self._remove_prev_message():
            await self.bot.send_message(chat_id=self.chat_id,
                                        text=self.bot_text,
                                        reply_markup=None)

        # send message with image and markup.
        await self._send_message()

        # remove image file on filesystem
        await self.__remove_file()

        return None
