from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.reply.bot_commands import bot_commands
from search_functions.functions import city_founding, ru_locale
import sys


def city_markup(message, bot):
	if ru_locale(message.text):
		locale = 'ru_RU'
	else:
		locale = 'en_US'
	cities = city_founding(message.text, locale)
	if cities:
		# Функция "city_founding" уже возвращает список словарей с нужным именем и id
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['hotels_key'] = {}
		destinations = InlineKeyboardMarkup()
		for num, city in enumerate(cities, 1):
			data['hotels_key'][f'key_{str(num)}'] = f'{city["city_name"]}|{city["destination_id"]}'
			# data['hotels_key'][f'key_{str(num)}'] = {'city_name': f'{city["city_name"]}',
			#                                          'destination_id': f'{city["destination_id"]}'}
			# print('Строка: ', sys.getsizeof(f'{city["city_name"]}|{city["destination_id"]}'))
			# print('Словарь: ', sys.getsizeof({'city_name': f'{city["city_name"]}',
			#                                   'destination_id': f'{city["destination_id"]}'}))
			# print('______________________________') словарь занимает в 2 раза больше памяти по сравнению со строкой
			# Вопрос насколько быстрее отрабатывает следующий код:
			# loc_name = data['hotels_key'][call.data].split('|')[0]
			# loc_id = data['hotels_key'][call.data].split('|')[-1]
			# по сравнению с этим:
			# loc_name = data['hotels_key'][call.data]['city_name']
			# loc_id = data['hotels_key'][call.data]['destination_id']
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
		bot.send_message(message.from_user.id, 'Пустая выборка! Попробуйте еще раз.',
		                 reply_markup=bot_commands())
