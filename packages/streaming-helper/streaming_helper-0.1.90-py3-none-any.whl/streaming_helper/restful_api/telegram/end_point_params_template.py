# -*- coding: utf-8 -*-


def basic_https() -> str:
    return f"https://api.telegram.org/bot"


def message_end_point(
    bot_token: str,
    bot_chatID: str,
    bot_message: str,
) -> str:

    return (
        bot_token
        + ("/sendMessage?chat_id=")
        + bot_chatID
        + ("&parse_mode=HTML&text=")
        + str(bot_message)
    )
