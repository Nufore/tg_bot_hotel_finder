from telebot.types import Message

from loader import bot


@bot.message_handler(state=None)
def bot_echo(message: Message) -> None:
    """
    Эхо хендлер, куда летят текстовые сообщения без указанного состояния
    :param message: Сообщение от пользователя
    :return:
    """
    bot.reply_to(message, "Эхо без состояния или фильтра.\nСообщение: "
                          f"{message.text}")
