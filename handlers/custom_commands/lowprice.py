from telebot.types import Message, ReplyKeyboardRemove
from loader import bot
from states.state_information import UserInfoState
from keyboards.inline.city_choise import get_city
from datetime import datetime


@bot.message_handler(commands=['lowprice'])
def lowprice(message: Message) -> None:
    """
    Хендлер обработки команды /lowprice
    :param message: Сообщение от пользователя
    :return:
    """
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['sortOrder'] = {'order': 'PRICE',
                             'datetime': datetime.now().replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')}

    bot.send_message(message.from_user.id, 'Укажите город, где будет проводиться поиск',
                     reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_city, bot)
