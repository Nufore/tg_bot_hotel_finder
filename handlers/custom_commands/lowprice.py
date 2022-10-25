from telebot.types import Message
from loader import bot, LSTEP
from states.lowprice_information import UserInfoState
from telegram_bot_calendar import DetailedTelegramCalendar
from handlers.callback_handlers import callback_query_handlers
from handlers.message_handlers import message_handlers


@bot.message_handler(commands=['lowprice'])
def lowprice(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Введите даты заезда/выезда')
    calendar, step = DetailedTelegramCalendar(calendar_id=1).build()
    bot.send_message(message.from_user.id,
                     f"Укажите {LSTEP[step]}",
                     reply_markup=calendar)

    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['sortOrder'] = 'PRICE'


# @bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
# def calend_checkin(call):
#     result, keyboard, step = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=1).process(call.data)
#     if not result and keyboard:
#         bot.edit_message_text(f"Укажите {LSTEP[step]}",
#                               call.message.chat.id,
#                               call.message.message_id,
#                               reply_markup=keyboard)
#     elif result:
#         bot.edit_message_text(f"Дата заезда {result}",
#                               call.message.chat.id,
#                               call.message.message_id)
#
#         with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
#             data['checkin'] = result
#
#         calendar, step = DetailedTelegramCalendar(calendar_id=2).build()
#         bot.send_message(call.message.chat.id,
#                          f"Укажите {LSTEP[step]}",
#                          reply_markup=calendar)


# @bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
# def calend_checkout(call):
#     result, keyboard, step = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=2).process(call.data)
#     if not result and keyboard:
#         bot.edit_message_text(f"Укажите {LSTEP[step]}",
#                               call.message.chat.id,
#                               call.message.message_id,
#                               reply_markup=keyboard)
#     elif result:
#         bot.edit_message_text(f"Дата выезда {result}",
#                               call.message.chat.id,
#                               call.message.message_id)
#
#         with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
#             data['checkout'] = result
#
#         bot.send_message(call.message.chat.id, 'Укажите город, где будет проводиться поиск')
#         bot.register_next_step_handler(call.message, city, bot)


# @bot.callback_query_handler(func=lambda call: call.data.isdigit(), state=UserInfoState.city)
# def get_specify_city(call):
#     bot.answer_callback_query(call.id)
#     bot.send_message(call.from_user.id,
#                      f'Город записал. {call.data}\nТеперь введите кол-во отелей',
#                      reply_markup=get_number())
#     bot.set_state(call.from_user.id, UserInfoState.number_of_hotels, call.message.chat.id)
#
#     with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
#         data['city'] = call.data


# @bot.callback_query_handler(func=lambda call: call.data.isdigit(), state=UserInfoState.number_of_hotels)
# def get_numbers_h(call):
#     bot.answer_callback_query(call.id)
#
#     bot.send_message(call.from_user.id,
#                      'Кол-во отелей записал.\nНужно ли выводить фото для каждого отеля?',
#                      reply_markup=request_photo())
#     bot.set_state(call.from_user.id, UserInfoState.is_need_photos, call.message.chat.id)
#
#     with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
#         data['number_of_hotels'] = call.data


# @bot.callback_query_handler(func=lambda call: call.data.isdigit(), state=UserInfoState.number_of_photos)
# def get_numbers_p(call):
#     bot.answer_callback_query(call.id)
#     bot.send_message(call.from_user.id, 'Кол-во фото записал.')
#     with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
#         data['number_of_photos'] = call.data
#
#     text = get_text(data, 'collected_data_1')
#     bot.send_message(call.from_user.id, text)
#
#     result = hotel_founding(data)
#     if result:
#         for res in result:
#             text = get_text(res, 'output_data')
#             try:
#                 media = get_photos(res["id"], int(data["number_of_photos"]), text)
#                 bot.send_media_group(call.from_user.id, media=media)
#             except Exception as e:
#                 print('bot.send_media_group')
#                 bot.send_message(call.from_user.id, 'Не удалось выгрузить фото отеля\n' + text,
#                                  parse_mode='HTML')
#     else:
#         bot.send_message(call.from_user.id, 'Request data not found :(')
#
#     bot.delete_state(call.from_user.id, call.message.chat.id)


# @bot.message_handler(state=UserInfoState.number_of_hotels)
# def get_number_of_hotels(message: Message) -> None:
#     if message.text.isdigit() and int(message.text) > 0:
#         bot.send_message(message.from_user.id,
#                          'Кол-во отелей записал.\nНужно ли выводить фото для каждого отеля?',
#                          reply_markup=request_photo())
#         bot.set_state(message.from_user.id, UserInfoState.is_need_photos, message.chat.id)
#
#         with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#             data['number_of_hotels'] = message.text
#     else:
#         bot.send_message(message.from_user.id, 'Введите число отелей для поиска отличное от нуля')
#
#
# @bot.message_handler(content_types=['text'], state=UserInfoState.is_need_photos)
# def get_is_need_photos(message: Message) -> None:
#     if message.text.isalpha() and message.text == 'Да':
#         bot.set_state(message.from_user.id, UserInfoState.number_of_photos, message.chat.id)
#         bot.send_message(message.from_user.id, 'Нужны ли фото записал.', reply_markup=ReplyKeyboardRemove())
#         bot.send_message(message.from_user.id, 'Укажите кол-во фото для каждого отеля',
#                          reply_markup=get_number())
#
#         with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#             data['is_need_photos'] = message.text
#
#     elif message.text.isalpha() and message.text == 'Нет':
#         with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#             data['is_need_photos'] = message.text
#         text = get_text(data, 'collected_data_2')
#         bot.send_message(message.from_user.id, text, reply_markup=ReplyKeyboardRemove())
#
#         result = hotel_founding(data)
#         if result:
#             for res in result:
#                 text = get_text(res, 'output_data')
#                 bot.send_message(message.from_user.id, text, parse_mode='HTML')
#         else:
#             bot.send_message(message.from_user.id, 'Request data not found :(')
#
#         bot.delete_state(message.from_user.id, message.chat.id)
#     else:
#         bot.send_message(message.from_user.id, 'Введите "Да" или "Нет"')
#
#
# @bot.message_handler(content_types=['text'], state=UserInfoState.number_of_photos)
# def get_number_of_photos(message: Message) -> None:
#     if message.text.isdigit() and int(message.text) > 0:
#         bot.send_message(message.from_user.id, 'Кол-во фото записал.')
#
#         with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#             data['number_of_photos'] = message.text
#
#         text = get_text(data, 'collected_data_1')
#         bot.send_message(message.from_user.id, text)
#
#         result = hotel_founding(data)
#         if result:
#             for res in result:
#                 text = get_text(res, 'output_data')
#                 try:
#                     media = get_photos(res["id"], int(data["number_of_photos"]), text)
#                     bot.send_media_group(message.from_user.id, media=media)
#                 except Exception as e:
#                     print('bot.send_media_group')
#                     bot.send_message(message.from_user.id, 'Не удалось выгрузить фото отеля\n' + text, parse_mode='HTML')
#         else:
#             bot.send_message(message.from_user.id, 'Request data not found :(')
#
#         bot.delete_state(message.from_user.id, message.chat.id)
#     else:
#         bot.send_message(message.from_user.id, 'Введите число фотографий отличное от нуля')
