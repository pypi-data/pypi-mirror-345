from urllib.parse import urlencode
from requests import get as requests_get
from telebot.types import ForceReply
from mizuhara.core.handlers.handlers import ResultShowingWithInlineMarkup
from mizuhara.translation import translate


class ReceiverWithLocation(ResultShowingWithInlineMarkup):
    """
    ReceiverWithLocation:

    this class is responsible for sending location of telegram user.
    when user sends its location on Attachment > location, telegram can grap the location information(latitude and longitude).

    this class can be used to update current location or record travel routes and so on.
    user must send its location manually.
    """

    def __init__(self, types, **kwargs):
        super(ReceiverWithLocation, self).__init__(types, **kwargs)
        self.location = None


    async def get_location(self) -> bool:
        """
        this method is charge of sending preamble message and receiving user's current location.
        you can reprocess the location information with self.location:dict

        :return: bool
        """

        if getattr(self.types, "location", None) is not None:
            self.location = self.types.location.to_dict()
            await self.post_process()

            await self.bot.send_message(chat_id=self.chat_id,
                                        text=self.bot_text)
            return True

        await super().send_message()
        return False


class SenderWithLocation(ResultShowingWithInlineMarkup):
    """
    SenderWithLocation:

    this class is charge of sending location information with latitude and longitude.
    the dev must set the self.latitude and self.longitude by overriding pre_process.
    """

    def __init__(self, types, **kwargs):
        super(SenderWithLocation, self).__init__(types, **kwargs)
        self.latitude = None
        self.longitude = None

    async def pre_process(self):
        """
        by overriding this method, set the latitude and longitude (float).

        :return:
        """
        pass

    async def send_message(self):
        await self.pre_process()

        if self.latitude is None or self.longitude is None:
            raise ValueError(translate(domain="default_warnings",
                                       key="warn_location_not_found",
                                       language_code=self.language))

        if not isinstance(self.latitude, float) or not isinstance(self.longitude, float):
            raise ValueError(translate(domain="default_exceptions",
                                       key="err_location_wrong_type",
                                       language_code=self.language))

        await self.bot.send_location(chat_id=self.chat_id,
                                     latitude=self.latitude,
                                     longitude=self.longitude,
                                     reply_markup=self.bot_markup)
        return None


class SendWithLocationName(ResultShowingWithInlineMarkup):
    """
    SendWithLocationName

    this class is charge of searching location name, address or postal number, which is typed by telegram user.
    this class will return location data with longitude and latitude to telegram user.
    this class contains 3rd API service(Nominatim OpenStreetMap)

    """

    GEO_INFO_API_URL: str = "https://nominatim.openstreetmap.org/search?"

    def __init__(self, types, **kwargs):
        super(SendWithLocationName, self).__init__(types, **kwargs)
        self.latitude = None
        self.longitude = None

    async def send_message(self) -> None:
        # if user input the search query.
        if getattr(self.types, "message", None) is None:
            await self._remove_prev_message()
            await self.post_process()

        # initial stage that the user click the search location callback data.
        else:
            self.bot_text = translate(domain="default_handlers",
                                      key="guide_force_reply_continue",
                                      language_code=self.language)
            await super().send_message()
            self.bot_markup = ForceReply()
            await self.bot.send_message(chat_id=self.chat_id,
                                        text=translate(domain="default_handlers",
                                                       key="guide_location_input",
                                                       language_code=self.language),
                                        reply_markup=ForceReply())
        return None

    async def post_process(self) -> None:
        """
        this method calls Nominatim API and provide user to location information.

        :return:
        """

        headers = {"User-Agent": "telebot_framework"}
        params = {
            "q": self.client_response,
            "format": "jsonv2",
            "limit": 1
        }
        response = requests_get(url=self.GEO_INFO_API_URL + urlencode(params),
                                headers=headers)

        if response.status_code == 200 and len(response.json()) != 0:
            location = response.json()[0]
            address = location.get("display_name")
            self.latitude = location.get("lat")
            self.longitude = location.get("lon")
            text = translate(domain="default_handlers",
                             key="result_location_search",
                             language_code=self.language).format(self.client_response, address)

            await self.bot.send_message(chat_id=self.chat_id,
                                        text=text)

            await self.bot.send_location(chat_id=self.chat_id,
                                         latitude=self.latitude,
                                         longitude=self.longitude,
                                         reply_markup=self.bot_markup)
            return None

        else:
            self.bot_text = translate(domain="default_warnings",
                                       key="warn_location_not_found",
                                       language_code=self.language)

        if await self._remove_prev_message():
            await self.bot.send_message(chat_id=self.chat_id,
                                        text=self.bot_text,
                                        reply_markup=self.bot_markup)
        return None
