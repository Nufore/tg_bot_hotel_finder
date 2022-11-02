from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from search_functions.functions import city_founding


def city_markup(message, bot):
	cities = city_founding(message.text)
	if cities:
		# Функция "city_founding" уже возвращает список словарей с нужным именем и id
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['hotels_key'] = {}
		destinations = InlineKeyboardMarkup()
		for num, city in enumerate(cities, 1):
			data['hotels_key'][f'key_{str(num)}'] = f'{city["city_name"]}|{city["destination_id"]}'
			destinations.add(InlineKeyboardButton(text=city["city_name"],
			                                      callback_data=f'key_{str(num)}'))
		return destinations
	return


def city(message, bot):
	markup = city_markup(message, bot)
	if markup:
		bot.send_message(message.from_user.id, 'Уточните, пожалуйста:',
		                 reply_markup=markup)  # Отправляем кнопки с вариантами
	else:
		bot.send_message(message.from_user.id, 'Пустая выборка! Попробуйте еще раз /lowprice')
