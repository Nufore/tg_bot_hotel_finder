from loader import bot
from config_data.config import NO_PHOTO
from telebot.types import Message, ReplyKeyboardRemove
from states.state_information import UserInfoState
from search_functions.functions import get_text, get_request_data
from keyboards.inline.get_numbers import get_number
from keyboards.reply.is_need_photo import request_photo
from keyboards.reply.min_max_price import min_max_price


@bot.message_handler(state=UserInfoState.minMaxPrice)
def get_min_max_price(message: Message) -> None:
    if message.text.isdigit() and int(message.text) > 0:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if data['min_max_price']['minPrice'] and (int(message.text) >= int(data['min_max_price']['minPrice'])):
                data['min_max_price']['maxPrice'] = message.text
                bot.delete_message(message.from_user.id, message.id)
                for i in reversed(range(1, len(data['min_max_price']['message_id']))):
                    bot.delete_message(message.from_user.id, data['min_max_price']['message_id'].pop(i))
                bot.edit_message_text(f'Диапазон цен: '
                                      f'{data["min_max_price"]["minPrice"]}-{data["min_max_price"]["maxPrice"]}$',
                                      message.from_user.id,
                                      data['min_max_price']['message_id'][0])
                bot.set_state(message.from_user.id, UserInfoState.distance, message.chat.id)
                bot.send_message(message.from_user.id, 'COOL', reply_markup=ReplyKeyboardRemove())
            elif not data['min_max_price']['minPrice']:
                data['min_max_price']['minPrice'] = message.text
                bot.delete_message(message.from_user.id, message.id)
                for i in reversed(range(2, len(data['min_max_price']['message_id']))):
                    bot.delete_message(message.from_user.id, data['min_max_price']['message_id'].pop(i))
                bot.edit_message_text(f'Диапазон цен\nЦена от: {data["min_max_price"]["minPrice"]}',
                                      message.from_user.id,
                                      data['min_max_price']['message_id'][0])
                bot.delete_message(message.from_user.id, data['min_max_price']['message_id'].pop(1))
                message_3_id = bot.send_message(message.from_user.id, 'Цена до:',
                                                reply_markup=min_max_price(mltp=int(data['min_max_price']['minPrice'])))
                data['min_max_price']['message_id'].append(message_3_id.message_id)
            else:
                data['min_max_price']['message_id'].append(message.message_id)
                bot_message = bot.send_message(message.from_user.id, 'Максимальная цена должна быть больше минимальной')
                data['min_max_price']['message_id'].append(bot_message.message_id)
    else:
        bot_message = bot.send_message(message.from_user.id, 'Укажите цену больше 0')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['min_max_price']['message_id'].append(message.message_id)
            data['min_max_price']['message_id'].append(bot_message.message_id)


@bot.message_handler(state=UserInfoState.number_of_hotels)
def get_number_of_hotels(message: Message) -> None:
    """
    Хендлер, обрабатывающий количество указанных пользователем отелей (пользователь вводил данные с клавиатуры)
    :param message: Сообщение от пользователя
    :return:
    """
    if message.text.isdigit() and int(message.text) > 0:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['number_of_hotels']['data'] = message.text

        bot.edit_message_text('Укажите кол-во отелей', message.chat.id, data['number_of_hotels']['message_id'])
        bot.set_state(message.from_user.id, UserInfoState.is_need_photos, message.chat.id)

        message_id = bot.send_message(message.from_user.id, 'Нужно ли выводить фото для каждого отеля?',
                                      reply_markup=request_photo())
        data['is_need_photos'] = {'data': None,
                                  'message_id': message_id.message_id,
                                  'markup': 'reply'}

    else:
        bot.send_message(message.from_user.id, 'Введите число отелей для поиска отличное от нуля')


@bot.message_handler(content_types=['text'], state=UserInfoState.is_need_photos)
def get_is_need_photos(message: Message) -> None:
    """
    Хендлер, обрабатывающий данные от пользователя по выводу фотографий
    Если фото не нужны, то выводим собранную информацию по отелям
    :param message: Сообщение от пользователя
    :return:
    """
    if message.text.isalpha() and message.text == 'Да':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['is_need_photos']['data'] = message.text
        if data['is_need_photos']['markup'] == 'inline':
            bot.edit_message_text("Нужно ли выводить фото для каждого отеля?",
                                  message.chat.id, data['is_need_photos']['message_id'])
        bot.set_state(message.from_user.id, UserInfoState.number_of_photos, message.chat.id)
        message_id = bot.send_message(message.from_user.id, 'Укажите кол-во фото', reply_markup=get_number())
        data['number_of_photos'] = {'data': None,
                                    'message_id': message_id.message_id}

    elif message.text.isalpha() and message.text == 'Нет':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['is_need_photos']['data'] = message.text
        bot.send_message(message.from_user.id, 'Ищу отели...', reply_markup=ReplyKeyboardRemove())

        result = get_request_data(data=data)
        if result:
            for res in result:
                text = get_text(res)
                bot.send_message(message.from_user.id, text, parse_mode='HTML', disable_web_page_preview=True)
        else:
            bot.send_message(message.from_user.id, 'Request data not found :(')

        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Введите "Да" или "Нет"')


@bot.message_handler(content_types=['text'], state=UserInfoState.number_of_photos)
def get_number_of_photos(message: Message) -> None:
    """
    Хендлер обработки количества фото и вывода информации по отелям с фото
    :param message: Сообщение от пользователя
    :return:
    """
    if message.text.isdigit() and int(message.text) > 0:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['number_of_photos']['data'] = message.text

        bot.edit_message_text('Укажите кол-во фото', message.chat.id, data['number_of_photos']['message_id'])
        bot.send_message(message.from_user.id, 'Ищу отели...', reply_markup=ReplyKeyboardRemove())

        result = get_request_data(data=data)
        if result:
            for res in result:
                text = get_text(res)
                try:
                    media = get_request_data(endpoint_id=res["id"],
                                             number_of_photos=int(data["number_of_photos"]['data']),
                                             text=text)
                    bot.send_media_group(message.from_user.id, media=media)
                except Exception as e:
                    print(e.__str__())
                    bot.send_photo(message.from_user.id,
                                   photo=open(file=NO_PHOTO, mode='rb'),
                                   caption=text,
                                   parse_mode='HTML')
        else:
            bot.send_message(message.from_user.id, 'Request data not found :(')

        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Введите число фотографий отличное от нуля')
