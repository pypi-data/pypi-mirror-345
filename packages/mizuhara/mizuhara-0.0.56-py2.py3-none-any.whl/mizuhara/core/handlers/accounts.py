from mizuhara.core.handlers.handlers import (ReceiverBasic,
                                             ReceiverWithForceReply,
                                             CLIENT_INFO)
from mizuhara.translation import translate


class SignInBasic(ReceiverWithForceReply):
    """
    SignInBasic:

    this class is a template for signin process.
    basic fields are compromised by "email" and "password".
    user will type there email and password on your bot chatroom,
    and it would be stored in CLIENT_INFO[self.chat_id]["data"].

    if you need to change field's name or add more fields, please override __init__() method and change inner Meta class.
    this class requires developers to override post_process() method to call API etc.

    please do not forget to update CLIENT_INFO[self.chat_id]["is_signin"] to True in post_process(),
    if the user success to signin.
    """

    class Meta:
        fields = ["email", "password"]
        fields_text = {
            "email": "signin_email",
            "password": "signin_password",
        }
        fields_regex = {
            "email": "^.+@.+\\..+$",
        }
        fields_error_msg = {
            "email": "warn_email_format",
        }

    def __init__(self, types, **kwargs):
        super(SignInBasic, self).__init__(types, **kwargs)

    async def get_client_data(self) -> bool:
        if not CLIENT_INFO[self.chat_id].get("is_signin"):
            return await super().get_client_data()

        else:
            await self.bot.send_message(chat_id=self.chat_id,
                                        text=translate(domain="warnings",
                                                       key="warn_already_signin",
                                                       types=self.types))
            return True


class SignOutBasic(ReceiverBasic):
    """
    SignOutBasic:

    this class is template for sign out process.
    this class requires developers to override post_process() method to call API etc.
    """

    async def pre_process(self) -> bool:
        if not CLIENT_INFO[self.chat_id].get("is_signin"):
            self.bot_text = translate(domain="warnings",
                                      key="warn_already_signout",
                                      types=self.types)
            return False
        return True

    async def send_message(self) -> None:
        if await self.pre_process():
            await self.post_process()

        await super().send_message()
        return None

    async def post_process(self):
        pass


class SignUpBasic(ReceiverWithForceReply):
    """
    SignUpBasic:

    this class is a template for sign up process.
    it provides fields 'email' and 'password' as a default to allow user to sign up.

    it is possible to edit regex and error message to check user input.
    if you want to change values in Meta class, just override __init__() and change values.
    """

    class Meta:
        fields = ["email", "password"]
        fields_text = {
            "email": "signup_email",
            "password": "signup_password",
        }
        fields_regex = {
            "email": ("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",),
            "password": (
                "[A-Z]+",
                "[a-z]+",
                "[0-9]+",
                "[!@#$%^&*()_+\\-=]+",
                ".{8,}",
            )
        }
        fields_error_msg = {
            "email": "warn_email_format",
            "password": (
                "warn_password_no_upper",
                "warn_password_no_lower",
                "warn_password_no_digit",
                "warn_password_no_special",
                "warn_password_no_minimal",
            )
        }

    def __init__(self, types, **kwargs):
        super(SignUpBasic, self).__init__(types, **kwargs)


class DeleteAccountBasic(ReceiverWithForceReply):
    """
    DeleteAccountBasic:

    this class is a template for delete account process.
    it requires user to input password of account which the user would like to delete as a default.

    if you need to change field's name or add more fields, please override __init__() method and change inner Meta class.
    this class requires developers to override post_process() method to call API etc.
    """

    class Meta:
        fields = ["password"]
        fields_text = {
            "password": "delete_account"
        }

    def __init__(self, types, **kwargs):
        super(DeleteAccountBasic, self).__init__(types, **kwargs)
