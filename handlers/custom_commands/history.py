from telebot.types import Message, ReplyKeyboardRemove

from database.db_connect import get_history_data
from loader import bot


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    """
    Хендлер обработки команды /history
    Выводит историю поиска пользователя
    :param message: Сообщение от пользователя
    :return:
    """

    ReplyKeyboardRemove()
    hist_list = get_history_data(message.from_user.id)
    if hist_list:
        for text in hist_list:
            bot.send_message(message.from_user.id, text)
    else:
        bot.send_message(message.from_user.id, 'Пока не было запросов.')
