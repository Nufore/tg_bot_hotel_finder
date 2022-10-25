from telebot.types import Message
from loader import bot, LSTEP
from states.lowprice_information import UserInfoState
from telegram_bot_calendar import DetailedTelegramCalendar
from handlers.callback_handlers import callback_query_handlers
from handlers.message_handlers import message_handlers


@bot.message_handler(commands=['highprice'])
def lowprice(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Введите даты заезда/выезда')
    calendar, step = DetailedTelegramCalendar(calendar_id=1).build()
    bot.send_message(message.from_user.id,
                     f"Укажите {LSTEP[step]}",
                     reply_markup=calendar)

    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['sortOrder'] = 'PRICE_HIGHEST_FIRST'
