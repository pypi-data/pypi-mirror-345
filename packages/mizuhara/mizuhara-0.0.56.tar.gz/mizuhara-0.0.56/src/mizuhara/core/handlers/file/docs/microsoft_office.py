from mizuhara.core.handlers.file.docs import ReceiverWithDocs
from mizuhara.translation import translate


class ReceiverWithExcelFile(ReceiverWithDocs):
    """
    ReceiverWithExcelFile

    this class is charge of receiving MS Office Excel file from telegram user.
    """

    async def validate_file(self):
        if not self.file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            raise ValueError(translate(domain="default_warnings",
                                       key="warn_upload_not_excel",
                                       language_code=self.language))

        return None


class ReceiverWithPPTFile(ReceiverWithDocs):
    """
    ReceiverWithPPTFile

    this class is charge of receiving MS Office PPT file from telegram user.
    """

    async def validate_file(self):
        if not self.file_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            raise ValueError(translate(domain="default_warnings",
                                       key="warn_upload_not_ppt",
                                       language_code=self.language))


class ReceiverWithWordFile(ReceiverWithDocs):
    """
    ReceiverWithWordFile

    this class is charge of receiving MS Office Word file from telegram user.
    """

    async def validate_file(self):
        if not self.file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            raise ValueError(translate(domain="default_warnings",
                                       key="warn_upload_not_word",
                                       language_code=self.language))

        return None
