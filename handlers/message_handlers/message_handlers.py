from database.db_connect import save_history_data
from loader import bot
from config_data.config import NO_PHOTO, LOG_PATH
from telebot.types import Message, ReplyKeyboardRemove
from states.state_information import UserInfoState
from search_functions.functions import get_text, get_request_data
from keyboards.inline.get_numbers import get_number
from keyboards.reply.is_need_photo import request_photo
from keyboards.reply.min_max_price import min_max_price
from loguru import logger


logger.add(LOG_PATH, format="{time} {level} {message}", level="ERROR", serialize=True)


@bot.message_handler(state=UserInfoState.minMaxPrice)
def get_min_max_price(message: Message) -> None:
    """
    Хендлер, обработка данных по вводу диапазона цен для команды /highprice
    :param message: Сообщение от пользователя
    :return:
    """
    try:
        message_text = float(message.text.replace(',', '.'))
        if message_text > 0:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                if data['min_max_price']['minPrice'] and (message_text >= data['min_max_price']['minPrice']):
                    data['min_max_price']['maxPrice'] = message_text

                    bot.delete_message(message.from_user.id, message.id)
                    for i in reversed(range(1, len(data['min_max_price']['message_id']))):
                        bot.delete_message(message.from_user.id, data['min_max_price']['message_id'].pop(i))

                    bot.edit_message_text(f'Диапазон цен: '
                                          f'{data["min_max_price"]["minPrice"]}-{data["min_max_price"]["maxPrice"]}$',
                                          message.from_user.id,
                                          data['min_max_price']['message_id'][0])

                    bot.set_state(message.from_user.id, UserInfoState.distance, message.chat.id)
                    bot_message = bot.send_message(message.from_user.id, 'Укажите максимальное расстояние от центра:')
                    ReplyKeyboardRemove()
                    data['distance'] = {'distance': None,
                                        'message_id': [bot_message.message_id]}

                elif not data['min_max_price']['minPrice']:
                    data['min_max_price']['minPrice'] = message_text

                    bot.delete_message(message.from_user.id, message.id)
                    for i in reversed(range(2, len(data['min_max_price']['message_id']))):
                        bot.delete_message(message.from_user.id, data['min_max_price']['message_id'].pop(i))

                    bot.edit_message_text(f'Диапазон цен\nЦена от: {data["min_max_price"]["minPrice"]}',
                                          message.from_user.id,
                                          data['min_max_price']['message_id'][0])

                    message_3_id = bot.send_message(message.from_user.id, 'Цена до:',
                                                    reply_markup=min_max_price(
                                                        mltp=data['min_max_price']['minPrice']))
                    bot.delete_message(message.from_user.id, data['min_max_price']['message_id'].pop(1))
                    data['min_max_price']['message_id'].append(message_3_id.message_id)
                else:
                    data['min_max_price']['message_id'].append(message.message_id)
                    bot_message = bot.send_message(message.from_user.id,
                                                   'Максимальная цена должна быть больше минимальной')
                    data['min_max_price']['message_id'].append(bot_message.message_id)
        else:
            bot_message = bot.send_message(message.from_user.id, 'Укажите цену больше 0')
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['min_max_price']['message_id'].append(message.message_id)
                data['min_max_price']['message_id'].append(bot_message.message_id)
    except ValueError:
        bot_message = bot.send_message(message.from_user.id, 'Укажите число в форматах 0.1 / 0,1 / 1 / 10')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['min_max_price']['message_id'].append(message.message_id)
            data['min_max_price']['message_id'].append(bot_message.message_id)


@bot.message_handler(state=UserInfoState.distance)
def get_distance(message: Message) -> None:
    """
    Хендлер, обработка данных по вводу максимального расстояния от центра для команды /highprice
    :param message: Сообщение от пользователя
    :return:
    """
    try:
        message_text = float(message.text.replace(',', '.'))
        if message_text > 0:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['distance']['distance'] = message_text
            bot.delete_message(message.from_user.id, message.id)
            for i in reversed(range(1, len(data['distance']['message_id']))):
                bot.delete_message(message.from_user.id, data['distance']['message_id'].pop(i))

            bot.edit_message_text(f'Максимальное расстояние от центра: {data["distance"]["distance"]}',
                                  message.from_user.id,
                                  data['distance']['message_id'][0])

            bot.set_state(message.from_user.id, UserInfoState.number_of_hotels, message.chat.id)
            message_id = bot.send_message(message.from_user.id, 'Укажите кол-во отелей', reply_markup=get_number())
            data['number_of_hotels'] = {'data': None,
                                        'message_id': message_id.message_id}
        else:
            bot_message = bot.send_message(message.from_user.id, 'Укажите расстояние больше 0')
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['distance']['message_id'].append(message.message_id)
                data['distance']['message_id'].append(bot_message.message_id)
    except ValueError:
        bot_message = bot.send_message(message.from_user.id, 'Укажите число в форматах 0.1 / 0,1 / 1 / 10')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['distance']['message_id'].append(message.message_id)
            data['distance']['message_id'].append(bot_message.message_id)


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

        if data.get("distance", None):
            result = [res for res in get_request_data(data=data)
                      if float(res["landmarks"][0]["distance"].replace(' miles', '').replace(' mile', ''))
                      <= data["distance"]["distance"] and
                      data['min_max_price']['minPrice']
                      <= res["ratePlan"]["price"]["exactCurrent"]
                      <= data['min_max_price']['maxPrice']]
            if len(result) > int(data["number_of_hotels"]["data"]):
                result = result[0:int(data["number_of_hotels"]["data"])]
        else:
            result = get_request_data(data=data)
        try:
            if result:
                hotels_list = []
                for res in result:
                    hotels_list.append(res["name"])
                    text = get_text(res)
                    bot.send_message(message.from_user.id, text, parse_mode='HTML', disable_web_page_preview=True)
                save_history_data(user_id=message.from_user.id,
                                  command=data["sortOrder"]["order"],
                                  loc=data["city"]["name"],
                                  hotels=hotels_list,
                                  date=data["sortOrder"]["datetime"])
            else:
                bot.send_message(message.from_user.id, 'Request data not found :(')
        except Exception as e:
            logger.error(e.__str__())

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

        if data.get("distance", None):
            result = [res for res in get_request_data(data=data)
                      if float(res["landmarks"][0]["distance"].replace(' miles', '').replace(' mile', ''))
                      <= data["distance"]["distance"] and
                      data['min_max_price']['minPrice']
                      <= res["ratePlan"]["price"]["exactCurrent"]
                      <= data['min_max_price']['maxPrice']]
            if len(result) > int(data["number_of_hotels"]["data"]):
                result = result[0:int(data["number_of_hotels"]["data"])]
        else:
            result = get_request_data(data=data)

        if result:
            hotels_list = []
            for res in result:
                hotels_list.append(res["name"])
                text = get_text(res)
                try:
                    media = get_request_data(endpoint_id=res["id"],
                                             number_of_photos=int(data["number_of_photos"]['data']),
                                             text=text)
                    bot.send_media_group(message.from_user.id, media=media)
                except Exception as e:
                    logger.error(e.__str__())
                    bot.send_photo(message.from_user.id,
                                   photo=open(file=NO_PHOTO, mode='rb'),
                                   caption=text,
                                   parse_mode='HTML')
            save_history_data(user_id=message.from_user.id,
                              command=data["sortOrder"]["order"],
                              loc=data["city"]["name"],
                              hotels=hotels_list,
                              date=data["sortOrder"]["datetime"])
        else:
            bot.send_message(message.from_user.id, 'Request data not found :(')

        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Введите число фотографий отличное от нуля')
