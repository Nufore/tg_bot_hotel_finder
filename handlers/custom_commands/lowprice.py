from telebot.types import Message, ReplyKeyboardRemove
from loader import bot
from states.lowprice_information import UserInfoState
from keyboards.reply.lowprice_is_need_photo import request_photo
from keyboards.inline.city_choise import city, hotel_founding, get_photos, get_text


@bot.message_handler(commands=['lowprice'])
def lowprice(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['sortOrder'] = 'PRICE'

    bot.send_message(message.from_user.id, 'Укажите город, где будет проводиться поиск')
    bot.register_next_step_handler(message, city, bot)


@bot.callback_query_handler(func=lambda call: call.data.isdigit(), state=UserInfoState.city)
def get_specify_city(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, f'Город записал. {call.data}\nТеперь введите кол-во отелей')
    bot.set_state(call.from_user.id, UserInfoState.number_of_hotels, call.message.chat.id)

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['city'] = call.data


@bot.message_handler(state=UserInfoState.number_of_hotels)
def get_number_of_hotels(message: Message) -> None:
    if message.text.isdigit() and int(message.text) > 0:
        bot.send_message(message.from_user.id,
                         'Кол-во отелей записал.\nНужно ли выводить фото для каждого отеля?',
                         reply_markup=request_photo())
        bot.set_state(message.from_user.id, UserInfoState.is_need_photos, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['number_of_hotels'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Введите число отелей для поиска отличное от нуля')


@bot.message_handler(content_types=['text'], state=UserInfoState.is_need_photos)
def get_is_need_photos(message: Message) -> None:
    if message.text.isalpha() and message.text == 'Да':
        bot.send_message(message.from_user.id, 'Нужны ли фото записал.\nУкажите кол-во фото для каждого отеля?',
                         reply_markup=ReplyKeyboardRemove())
        bot.set_state(message.from_user.id, UserInfoState.number_of_photos, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['is_need_photos'] = message.text

    elif message.text.isalpha() and message.text == 'Нет':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['is_need_photos'] = message.text
        text = get_text(data, 'collected_data_2')
        bot.send_message(message.from_user.id, text, reply_markup=ReplyKeyboardRemove())

        result = hotel_founding(data)
        if result:
            for res in result:
                text = get_text(res, 'output_data')
                bot.send_message(message.from_user.id, text, parse_mode='HTML')
        else:
            bot.send_message(message.from_user.id, 'Request data not found :(')

        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Введите "Да" или "Нет"')


@bot.message_handler(content_types=['text'], state=UserInfoState.number_of_photos)
def get_number_of_photos(message: Message) -> None:
    if message.text.isdigit() and int(message.text) > 0:
        bot.send_message(message.from_user.id, 'Кол-во фото записал.')

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['number_of_photos'] = message.text

        text = get_text(data, 'collected_data_1')
        bot.send_message(message.from_user.id, text)

        result = hotel_founding(data)
        if result:
            for res in result:
                text = get_text(res, 'output_data')
                media = get_photos(res["id"], int(data["number_of_photos"]), text)
                bot.send_media_group(message.from_user.id, media=media)
        else:
            bot.send_message(message.from_user.id, 'Request data not found :(')

        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Введите число фотографий отличное от нуля')
