import importlib.resources
from yaml import safe_load
from os.path import exists
from mizuhara.core.routes import CLIENT_INFO


def translate(domain: str, key: str, types) -> str:
    """
    this function is charge of translate string, which is defined on yaml file in the same path, into another language_code.
    if you need customize, please create another yaml file on translation folder,
    and use this function to translate.

    :param domain: name or alternate path of yaml file.
    :param key: name of main key in yaml file.
    :param types: the type of telebot clients requests.
    :return: str
    """

    # convert file name to file system format.
    file_name = f"{domain.replace("_", "/")}.yml"

    # check if there's a user-defined translation file
    if exists(f"translation/{file_name}"):
        with open(f"translation/{file_name}", mode="r", encoding="utf-8") as file:
            content = safe_load(file) or {}

    # If no translation file exists, return the original key
    else:
        try:
            with importlib.resources.files("mizuhara.translation").joinpath(file_name).open("r",
                                                                                            encoding="utf-8") as file:
                content = safe_load(file) or {}
                if content.get(key.lower(), None) is None:
                    raise ModuleNotFoundError

        except (FileNotFoundError, ModuleNotFoundError):
            return key

    chat_id: int = types.from_user.id
    language_code: str = CLIENT_INFO.get(chat_id).language if CLIENT_INFO.get(chat_id) is not None \
        else types.from_user.language_code
    return content.get(key.lower(), {}).get(language_code, key)
