from telebot.types import Message
from loader import bot
from states.lowprice_information import UserInfoState
from keyboards.reply.lowprice_is_need_photo import request_photo
from keyboards.inline.city_choise import city


@bot.message_handler(commands=['lowprice'])
def lowprice(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите город, где будет проводиться поиск')
    bot.register_next_step_handler(message, city, bot)


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def get_specify_city(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, call.data)


@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
    if message.text.isalpha():
        bot.send_message(message.from_user.id, 'Город записал.\nТеперь введи кол-во отелей')
        bot.set_state(message.from_user.id, UserInfoState.number_of_hotels, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Название не может быть только из цифр')


@bot.message_handler(state=UserInfoState.number_of_hotels)
def get_number_of_hotels(message: Message) -> None:
    if message.text.isdigit():
        bot.send_message(message.from_user.id,
                         'Кол-во отелей записал.\nНужно ли выводить фото для каждого отеля?',
                         reply_markup=request_photo())
        bot.set_state(message.from_user.id, UserInfoState.is_need_photos, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['number_of_hotels'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Введите число отелей для поиска')


@bot.message_handler(content_types=['text'], state=UserInfoState.is_need_photos)
def get_is_need_photos(message: Message) -> None:
    if message.text.isalpha() and message.text == 'Да':
        bot.send_message(message.from_user.id, 'Нужны ли фото записал.\nУкажи кол-во фото для каждого отеля?')
        bot.set_state(message.from_user.id, UserInfoState.number_of_photos, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['is_need_photos'] = message.text
    elif message.text.isalpha() and message.text == 'Нет':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['is_need_photos'] = message.text
        text = f'Собранная информация: \n' \
               f'Город - {data["city"]}\nКол-во отелей - {data["number_of_hotels"]}\n' \
               f'Нужны ли фото - {data["is_need_photos"]}'
        msg = bot.send_message(message.from_user.id, text)
        bot.register_next_step_handler(msg, stop_state)
    else:
        bot.send_message(message.from_user.id, 'Введите "да" или "нет"')


@bot.message_handler(content_types=['text'], state=UserInfoState.number_of_photos)
def get_number_of_photos(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if data['is_need_photos'] == 'Да' and message.text.isdigit():
            bot.send_message(message.from_user.id, 'Кол-во фото записал.')
            data['number_of_photos'] = message.text
            text = f'Собранная информация: \n' \
                   f'Город - {data["city"]}\nКол-во отелей - {data["number_of_hotels"]}\n' \
                   f'Нужны ли фото - {data["is_need_photos"]}\nКол-во фото - {data["number_of_photos"]}'
            msg = bot.send_message(message.from_user.id, text)
            bot.register_next_step_handler(msg, stop_state)
        else:
            bot.send_message(message.from_user.id, 'Введите число фотографий')


def stop_state(message: Message) -> None:
    bot.delete_state(message.from_user.id, message.chat.id)
