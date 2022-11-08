import datetime
from loader import bot
from config_data.config import LSTEP, NO_PHOTO
from telebot.types import CallbackQuery, ReplyKeyboardRemove
from telegram_bot_calendar import DetailedTelegramCalendar
from states.state_information import UserInfoState
from search_functions.functions import get_text, get_request_data
from keyboards.inline.get_numbers import get_number
from keyboards.inline.yes_no_btn import yes_no


@bot.callback_query_handler(func=lambda call: call.data.startswith('key'), state=UserInfoState.city)
def get_specify_city(call: CallbackQuery) -> None:
    """
    callback хендлер, устанавливает id локации в data['city'], затем отправляет сообщение с календарем
    :param call: отклик пользователя
    :return:
    """
    bot.answer_callback_query(call.id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        loc_name = data['hotels_key'][call.data].split('|')[0]
        loc_id = data['hotels_key'][call.data].split('|')[-1]
    del data['hotels_key']
    data['city'] = loc_id
    bot.edit_message_text(f'Локация: {loc_name}', call.message.chat.id,
                          call.message.message_id)

    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru').build()
    bot.send_message(call.from_user.id,
                     f"Введите дату заезда\nУкажите {LSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def calend_checkin(call: CallbackQuery) -> None:
    """
    callback хендлер, создаем календарь с id=1 на запись даты заезда
    :param call: отклик пользователя
    :return:
    """
    bot.answer_callback_query(call.id)
    result, keyboard, step = DetailedTelegramCalendar(min_date=datetime.date.today(),
                                                      calendar_id=1,
                                                      locale='ru').process(call.data)
    if not result and keyboard:
        bot.edit_message_text(f"Введите дату заезда\nУкажите {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=keyboard)
    elif result:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['checkin'] = result
        calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru').build()
        bot.edit_message_text(f"Дата заезда {result}\nВведите дату выезда\nУкажите {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id, reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def calend_checkout(call: CallbackQuery) -> None:
    """
    callback хендлер, создаем календарь с id=2 на запись даты выезда
    :param call: отклик пользователя
    :return:
    """
    bot.answer_callback_query(call.id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        min_date = data['checkin']

    result, keyboard, step = DetailedTelegramCalendar(min_date=min_date + datetime.timedelta(days=1),
                                                      calendar_id=2,
                                                      locale='ru').process(call.data)
    if not result and keyboard:
        bot.edit_message_text(f"Дата заезда {min_date}\nВведите дату выезда\nУкажите {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=keyboard)
    elif result:
        bot.edit_message_text(f"Дата заезда {min_date}\nДата выезда {result}",
                              call.message.chat.id,
                              call.message.message_id)
        data['checkout'] = result
        bot.set_state(call.from_user.id, UserInfoState.number_of_hotels, call.message.chat.id)
        message_id = bot.send_message(call.from_user.id, 'Укажите кол-во отелей', reply_markup=get_number())
        data['number_of_hotels'] = {'data': None,
                                    'message_id': message_id.message_id}


@bot.callback_query_handler(func=lambda call: call.data.isdigit(), state=UserInfoState.number_of_hotels)
def get_numbers_h(call: CallbackQuery) -> None:
    """
    callback хендлер, сохраняем в состояние кол-во отелей для вывода
    :param call: отклик пользователя
    :return:
    """
    bot.answer_callback_query(call.id)

    bot.set_state(call.from_user.id, UserInfoState.is_need_photos, call.message.chat.id)

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['number_of_hotels']['data'] = call.data

    bot.edit_message_text(f"Кол-во отелей: {call.data}", call.message.chat.id, call.message.message_id)
    message_id = bot.send_message(call.message.chat.id, "Нужно ли выводить фото для каждого отеля?",
                                  reply_markup=yes_no())
    data['is_need_photos'] = {'data': None,
                              'message_id': message_id.message_id,
                              'markup': 'inline'}


@bot.callback_query_handler(func=lambda call: call.data.isalpha(), state=UserInfoState.is_need_photos)
def get_need_photos(call: CallbackQuery) -> None:
    """
    callback хендлер, обрабатывающий данные от пользователя по выводу фотографий
    Если фото не нужны, то выводим собранную информацию по отелям
    :param call: отклик пользователя
    :return:
    """
    bot.answer_callback_query(call.id)
    if call.data == 'Да':
        bot.set_state(call.from_user.id, UserInfoState.number_of_photos, call.message.chat.id)
        bot.edit_message_text(f"Вывод фото: {call.data}", call.message.chat.id, call.message.message_id)
        message_id = bot.send_message(call.message.chat.id, 'Укажите кол-во фото', reply_markup=get_number())

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['is_need_photos'] = call.data
            data['number_of_photos'] = {'data': None,
                                        'message_id': message_id.message_id}

    elif call.data == 'Нет':
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['is_need_photos'] = call.data
        bot.edit_message_text(f"Вывод фото: {call.data}", call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Ищу отели...', reply_markup=ReplyKeyboardRemove())
        result = get_request_data(data=data)
        if result:
            for res in result:
                text = get_text(res)
                bot.send_message(call.message.chat.id, text, parse_mode='HTML', disable_web_page_preview=True)
        else:
            bot.send_message(call.message.chat.id, 'Request data not found :(')

        bot.delete_state(call.from_user.id, call.message.chat.id)
    else:
        bot.send_message(call.message.chat.id, 'Введите "Да" или "Нет"')


@bot.callback_query_handler(func=lambda call: call.data.isdigit(), state=UserInfoState.number_of_photos)
def get_numbers_p(call: CallbackQuery) -> None:
    """
    callback хендлер обработки количества фото и вывода информации по отелям с фото
    :param call:
    :return: отклик пользователя
    """
    bot.answer_callback_query(call.id)
    bot.edit_message_text(f'Кол-во фото: {call.data}', call.message.chat.id, call.message.message_id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['number_of_photos']['data'] = call.data

    bot.send_message(call.message.chat.id, 'Ищу отели...', reply_markup=ReplyKeyboardRemove())

    result = get_request_data(data=data)
    if result:
        for res in result:
            text = get_text(res)
            try:
                media = get_request_data(endpoint_id=res["id"],
                                         number_of_photos=int(data["number_of_photos"]['data']),
                                         text=text)
                bot.send_media_group(call.from_user.id, media=media)
            except Exception as e:
                print(e.__str__())
                bot.send_photo(call.from_user.id,
                               photo=open(file=NO_PHOTO, mode='rb'),
                               caption=text,
                               parse_mode='HTML')
    else:
        bot.send_message(call.from_user.id, 'Request data not found :(')

    bot.delete_state(call.from_user.id, call.message.chat.id)
