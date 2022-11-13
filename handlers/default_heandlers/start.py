from telebot.types import Message

from keyboards.inline.help import inline_help
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    """
    Обработчик команды /start
    :param message: Сообщение от пользователя
    :return:
    """
    bot.send_message(message.from_user.id,
                     f"Привет, {message.from_user.full_name}!\n"
                     "Я бот по поиску отелей. Чтобы посмотреть, что я умею - нажми на /help",
                     reply_markup=inline_help())
