import datetime
from loader import bot
from config_data.config import LSTEP
from telebot.types import CallbackQuery
from telegram_bot_calendar import DetailedTelegramCalendar
from states.state_information import UserInfoState
from search_functions.functions import hotel_founding, get_photos, get_text
from keyboards.inline.get_numbers import get_number
from keyboards.inline.yes_no_btn import yes_no


@bot.callback_query_handler(func=lambda call: call.data.split('|')[-1].isdigit(), state=UserInfoState.city)
def get_specify_city(call: CallbackQuery):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(f'Локация: {call.data.split("|")[0]}', call.message.chat.id,
                          call.message.message_id)

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['city'] = call.data.split('|')[-1]

    calendar, step = DetailedTelegramCalendar(calendar_id=1).build()
    bot.send_message(call.from_user.id,
                     f"Введите дату заезда\nУкажите {LSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def calend_checkin(call: CallbackQuery):
    result, keyboard, step = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=1).process(call.data)
    if not result and keyboard:
        bot.edit_message_text(f"Введите дату заезда\nУкажите {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=keyboard)
    elif result:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['checkin'] = result
        calendar, step = DetailedTelegramCalendar(calendar_id=2).build()
        bot.edit_message_text(f"Дата заезда {result}\nВведите дату выезда\nУкажите {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id, reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def calend_checkout(call: CallbackQuery):
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        min_date = data['checkin']

    result, keyboard, step = DetailedTelegramCalendar(min_date=min_date + datetime.timedelta(days=1),
                                                      calendar_id=2).process(call.data)
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
        bot.send_message(call.from_user.id, 'Укажите кол-во отелей', reply_markup=get_number())


@bot.callback_query_handler(func=lambda call: call.data.isdigit(), state=UserInfoState.number_of_hotels)
def get_numbers_h(call: CallbackQuery):
    bot.answer_callback_query(call.id)

    bot.set_state(call.from_user.id, UserInfoState.is_need_photos, call.message.chat.id)

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['number_of_hotels'] = call.data

    bot.edit_message_text(f"Кол-во отелей: {call.data}", call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Нужно ли выводить фото для каждого отеля?", reply_markup=yes_no())


@bot.callback_query_handler(func=lambda call: call.data.isalpha(), state=UserInfoState.is_need_photos)
def get_need_photos(call: CallbackQuery) -> None:
    if call.data == 'Да':
        bot.set_state(call.from_user.id, UserInfoState.number_of_photos, call.message.chat.id)
        bot.edit_message_text(f"Вывод фото: {call.data}", call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Укажите кол-во фото',
                         reply_markup=get_number())

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['is_need_photos'] = call.data

    elif call.data == 'Нет':
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['is_need_photos'] = call.data
        bot.edit_message_text(f"Вывод фото: {call.data}", call.message.chat.id, call.message.message_id)

        result = hotel_founding(data)
        if result:
            for res in result:
                text = get_text(res, 'output_data')
                bot.send_message(call.message.chat.id, text, parse_mode='HTML', disable_web_page_preview=True)
        else:
            bot.send_message(call.message.chat.id, 'Request data not found :(')

        bot.delete_state(call.from_user.id, call.message.chat.id)
    else:
        bot.send_message(call.message.chat.id, 'Введите "Да" или "Нет"')


@bot.callback_query_handler(func=lambda call: call.data.isdigit(), state=UserInfoState.number_of_photos)
def get_numbers_p(call: CallbackQuery):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(f'Кол-во фото: {call.data}', call.message.chat.id, call.message.message_id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['number_of_photos'] = call.data

    result = hotel_founding(data)
    if result:
        for res in result:
            text = get_text(res, 'output_data')
            try:
                media = get_photos(res["id"], int(data["number_of_photos"]), text)
                bot.send_media_group(call.from_user.id, media=media)
            except Exception as e:
                print('bot.send_media_group failed')
                bot.send_message(call.from_user.id, 'Не удалось выгрузить фото отеля\n' + text,
                                 parse_mode='HTML', disable_web_page_preview=True)
    else:
        bot.send_message(call.from_user.id, 'Request data not found :(')

    bot.delete_state(call.from_user.id, call.message.chat.id)
