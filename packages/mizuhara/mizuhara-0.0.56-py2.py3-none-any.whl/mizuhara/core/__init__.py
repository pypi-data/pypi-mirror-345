

class UserInfo:
    """
    UserInfo:

    this class is charge of saving telegram user's information in mizuhara.core.routes.CLIENT_INFO

    * data: store the data which will be used for api calling.
    * info: store the data that would be frequently used.
    * index: this value would be used for InlineMarkupButton' pagination.
             this value is automatically assigned. do not use it directly.
    * language: this value will store the default language_code.
    * is_signin: place the user's signin status with bool value.
    * page: this value would be used for InlineMarkupButton' pagination.
            this value is automatically assigned. do not use it directly.
    * pre_route: this value display where the user come from in telebot application.
                 this value is automatically assigned. do not use it directly
    * route: this value display user's location in telebot application.
             this value is automatically assigned. do not use it directly.
    * result: store the other information which you want to use temporarily.

    """

    def __init__(self, types, **kwargs):
        self.chat_info = {
            "msg_name": "TLGR",
            "chat_id": str(types.from_user.id),
            "is_signed_in": True
        }
        self.data: dict = {}
        self.info: dict = {}
        self.index: int = 0
        self.language: str = types.from_user.language_code
        self.is_signin: bool = False
        self.page: int = 0
        self.pre_route: str = ""
        self.route: str = ""
        self.result: any = None

    def get(self, key: str, default=None):
        return self.__dict__.get(key, default)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k == "route":
                setattr(self, "pre_route", self.route)

            setattr(self, k, v)
