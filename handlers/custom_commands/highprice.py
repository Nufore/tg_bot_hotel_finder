from telebot.types import Message
from loader import bot
from states.state_information import UserInfoState
from keyboards.inline.city_choise import city


@bot.message_handler(commands=['highprice'])
def lowprice(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['sortOrder'] = 'PRICE_HIGHEST_FIRST'

    bot.send_message(message.from_user.id, 'Укажите город, где будет проводиться поиск')
    bot.register_next_step_handler(message, city, bot)
