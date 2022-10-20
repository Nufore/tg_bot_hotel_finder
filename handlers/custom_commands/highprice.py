from telebot.types import Message, ReplyKeyboardRemove
from loader import bot
from states.lowprice_information import UserInfoState
from keyboards.reply.lowprice_is_need_photo import request_photo
from keyboards.inline.city_choise import city, hotel_founding, get_photos, get_text


@bot.message_handler(commands=['highprice'])
def lowprice(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['sortOrder'] = 'PRICE_HIGHEST_FIRST'

    bot.send_message(message.from_user.id, 'Укажите город, где будет проводиться поиск')
    bot.register_next_step_handler(message, city, bot)
