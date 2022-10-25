from loader import bot
from telebot.types import Message, ReplyKeyboardRemove
from states.lowprice_information import UserInfoState
from search_functions.functions import hotel_founding, get_photos, get_text
from keyboards.inline.get_numbers import get_number
from keyboards.reply.lowprice_is_need_photo import request_photo


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
        bot.set_state(message.from_user.id, UserInfoState.number_of_photos, message.chat.id)
        bot.send_message(message.from_user.id, 'Нужны ли фото записал.', reply_markup=ReplyKeyboardRemove())
        bot.send_message(message.from_user.id, 'Укажите кол-во фото для каждого отеля',
                         reply_markup=get_number())

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
                try:
                    media = get_photos(res["id"], int(data["number_of_photos"]), text)
                    bot.send_media_group(message.from_user.id, media=media)
                except Exception as e:
                    print('bot.send_media_group')
                    bot.send_message(message.from_user.id, 'Не удалось выгрузить фото отеля\n' + text, parse_mode='HTML')
        else:
            bot.send_message(message.from_user.id, 'Request data not found :(')

        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Введите число фотографий отличное от нуля')