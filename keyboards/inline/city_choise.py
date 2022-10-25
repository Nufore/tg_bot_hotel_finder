from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from search_functions.functions import city_founding


def city_markup(message):
	cities = city_founding(message)
	if cities:
		# Функция "city_founding" уже возвращает список словарей с нужным именем и id
		destinations = InlineKeyboardMarkup()
		for city in cities:
			destinations.add(InlineKeyboardButton(text=city['city_name'],
			                                      callback_data=f'{city["destination_id"]}'))
		return destinations
	return


def city(message, bot):
	markup = city_markup(message.text)
	if markup:
		bot.send_message(message.from_user.id, 'Уточните, пожалуйста:',
		                 reply_markup=markup)  # Отправляем кнопки с вариантами
	else:
		bot.send_message(message.from_user.id, 'Пустая выборка! Попробуйте еще раз /lowprice')
