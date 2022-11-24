from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from keyboards.reply.bot_commands import bot_commands
from search_functions.functions import ru_locale, get_request_data


def city_markup(message: Message, bot) -> InlineKeyboardMarkup:
	"""
	Функция создания inline-клавиатуры для выбора локации/города
	:param message: Сообщение от пользователя при запросе указания города
	:param bot: TeleBot
	:return: Возвращает inline-клавиатуру с кнопками
	"""
	if ru_locale(message.text):
		locale = 'ru_RU'
	else:
		locale = 'en_US'

	cities = get_request_data(message=message.text, locale=locale)
	if cities:
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['hotels_key'] = {}
		destinations = InlineKeyboardMarkup()
		for num, city in enumerate(cities, 1):
			data['hotels_key'][f'key_{str(num)}'] = f'{city["city_name"]}|{city["destination_id"]}'
			destinations.add(InlineKeyboardButton(text=city["city_name"], callback_data=f'key_{str(num)}'))
		return destinations
	return


def get_city(message: Message, bot) -> None:
	"""
	Функция для отправки кнопок с выбором локации для пользователя
	:param message: Сообщение от пользователя при запросе указания города
	:param bot: TeleBot
	:return: Отправляем кнопки с вариантами или запрос на повторение действий
	"""
	markup = city_markup(message, bot)
	if markup:
		bot.send_message(message.from_user.id, 'Уточните, пожалуйста:', reply_markup=markup)
	else:
		bot.send_message(message.from_user.id, 'Пустая выборка! Попробуйте еще раз.', reply_markup=bot_commands())
