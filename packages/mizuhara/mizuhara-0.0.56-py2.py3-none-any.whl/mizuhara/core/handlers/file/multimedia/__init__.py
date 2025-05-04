from mizuhara.core.handlers.handlers import SenderWithBasic
from mizuhara.core.handlers.file.docs import ReceiverWithDocs


class ReceiverWithImage(ReceiverWithDocs):
    """
    ReceiverWithImage:

    this class is charge of getting uploaded image from telegram user.
    """

    def __init__(self, types, **kwargs):
        super(ReceiverWithImage, self).__init__(types, **kwargs)
        self.receive_type = "photo"

    async def get_uploaded_file(self) -> bool:

        if getattr(self.types, "photo", None):
            file_id = self.types.photo[-1].file_id

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


# SenderWithImage
class SenderWithImage(SenderWithBasic):
    """
    SenderWithImage:

    this class is charge of sending image from bot to user.
    this class receives the bytes data of original image file via API or the others,
    and convert data into the image content.

    the bot will send created image to telegram user.
    """

    async def _send_message(self) -> None:
        # send message with image and markup.
        with open(self.filepath, mode="rb") as f:
            await self.bot.send_photo(chat_id=self.chat_id,
                                      photo=f,
                                      reply_markup=self.bot_markup)

        return None
