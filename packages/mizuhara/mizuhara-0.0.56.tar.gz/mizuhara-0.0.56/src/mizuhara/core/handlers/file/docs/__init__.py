from mizuhara.core.handlers.handlers import SenderWithBasic
from mizuhara.core.handlers.handlers import ResultShowingWithInlineMarkup
from mizuhara.translation import translate


class ReceiverWithDocs(ResultShowingWithInlineMarkup):
    """
    ReceiverWithFile:

    this class is charge of getting uploaded file from telegram user.
    """

    class Meta:
        """
        this Meta class creates InlineMarkupButton to provide Cancel button to telegram user,
        who does not want to upload his or her file after executing file uploading process.
        """

        fields = ["Cancel"]
        fields_callback: dict = {
            "Cancel": None
        }

    def __init__(self, types, **kwargs):
        self.file: bytes|None = None
        self.file_name: str|None = None
        self.file_type: str|None = None
        super(ReceiverWithDocs, self).__init__(types, **kwargs)

    async def get_uploaded_file(self) -> bool:
        """
        this method receives an uploaded file from telegram user, validates file,
        and does post process with uploaded file.

        :return: bool
        """

        if getattr(self.types, "document", None):
            file_info = self.types.document
            file_id = file_info.file_id
            self.file_name = file_info.file_name
            self.file_type = file_info.mime_type

            try:
                await self.validate_file()

            except ValueError as e:
                self.bot_text = e
                self.bot_markup = None
                await super().send_message()
                return True

            else:
                get_file = await self.bot.get_file(file_id=file_id)
                self.file = await self.bot.download_file(file_path=get_file.file_path)
                await self.post_process()
                return True

        await super().send_message()
        return False

    async def validate_file(self):
        """
        please override this method to validate uploaded file.
        if there is an error, please RAISE ERROR with 'ValueError'

        :return: bool
        """

        pass

    async def post_process(self):
        """
        please override this method if you need to do some work with uploaded file.

        :return: bool
        """
        pass


class ReceiverWithCSVFile(ReceiverWithDocs):
    """
    ReceiverWithDocs:

    this class is charge of getting uploaded 'CSV' file from telegram user.
    """

    async def validate_file(self) -> None:
        if not self.file_type == "text/comma-separated-values":
            raise ValueError(translate(domain="default_warnings",
                                       key="warn_upload_not_csv",
                                       language_code=self.language))

        return None


class ReceiverWithJsonFile(ReceiverWithDocs):
    """
    ReceiverWithDocs:

    this class is charge of getting uploaded 'Json' file from telegram user.
    """

    async def validate_file(self) -> None:
        if not self.file_type == "application/json":
            raise ValueError(translate(domain="default_warnings",
                                       key="warn_upload_not_json",
                                       language_code=self.language))

        return None


class ReceiverWithMarkdownFile(ReceiverWithDocs):
    """
    ReceiverWithDocs:

    this class is charge of getting uploaded 'markdown' file from telegram user.
    """

    async def validate_file(self) -> None:
        if not self.file_type == "text/markdown":
            raise ValueError(translate(domain="default_warnings",
                                       key="warn_upload_not_markdown",
                                       language_code=self.language))

        return None


class ReceiverWithPDFFile(ReceiverWithDocs):
    """
    ReceiverWithDocs:

    this class is charge of getting uploaded 'PDF' file from telegram user.
    """

    async def validate_file(self) -> None:
        if not self.file_type == "application/pdf":
            raise ValueError(translate(domain="default_warnings",
                                       key="warn_upload_not_pdf",
                                       language_code=self.language))

        return None


class ReceiverWithTextFile(ReceiverWithDocs):
    """
    ReceiverWithDocs:

    this class is charge of getting uploaded 'text' file from telegram user.
    """

    async def validate_file(self) -> None:
        if not self.file_type == "text/plain":
            raise ValueError(translate(domain="default_warnings",
                                       key="warn_upload_not_text",
                                       language_code=self.language))

        return None


class ReceiverWithXMLFile(ReceiverWithDocs):
    """
    ReceiverWithDocs:

    this class is charge of getting uploaded 'XML' file from telegram user.
    """

    async def validate_file(self) -> None:
        if not self.file_type == "application/xml":
            raise ValueError(translate(domain="default_warnings",
                                       key="warn_upload_not_xml",
                                       language_code=self.language))

        return None


class ReceiverWithYamlFile(ReceiverWithDocs):
    """
    ReceiverWithDocs:

    this class is charge of getting uploaded 'YAML' file from telegram user.
    """

    async def validate_file(self) -> None:
        if not self.file_type == "application/octet-stream":
            raise ValueError(translate(domain="default_warnings",
                                       key="warn_upload_not_yaml",
                                       language_code=self.language))

        return None


class ReceiverWithZipFile(ReceiverWithDocs):
    """
    ReceiverWithDocs:

    this class is charge of getting uploaded 'Zip' file from telegram user.
    """

    async def validate_file(self) -> None:
        if not self.file_type == "application/zip":
            raise ValueError(translate(domain="default_warnings",
                                       key="warn_upload_not_zip",
                                       language_code=self.language))

        return None


class SenderWithDocs(SenderWithBasic):
    """
    SenderWithDocs:

    this class is charge of sending file from bot to user.
    this class receives the data which would be written in document or file,
    and convert data into the string content for download file.

    the bot will send created file to telegram user.
    please use it to create analysis report or summary after collecting data.
    """

    async def _send_message(self):
        with open(self.filepath, mode="r") as file:
            await self.bot.send_document(chat_id=self.chat_id,
                                         document=file,
                                         reply_markup=self.bot_markup)
        return None
