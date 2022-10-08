import requests
import re
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config_data import config


def city_founding(message):
	url = "https://hotels4.p.rapidapi.com/locations/v2/search"

	querystring = {"query": message}

	headers = {
		"X-RapidAPI-Key": config.RAPID_API_KEY,
		"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
	}
	response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
	pattern = r'(?<="CITY_GROUP",).+?[\]]'
	cities = list()

	find = re.search(pattern, response.text)
	if find:
		suggestions = json.loads(f"{{{find[0]}}}")
		for dest_id in suggestions['entities']:  # Обрабатываем результат
			clear_destination = re.sub("</span>", '', re.sub("<span class='highlighted'>", '', dest_id['caption']))
			cities.append({'city_name': clear_destination,
			               'destination_id': dest_id['destinationId']
			               }
			              )
	return cities


def city_markup(message):
	cities = city_founding(message)
	# Функция "city_founding" уже возвращает список словарей с нужным именем и id
	destinations = InlineKeyboardMarkup()
	for city in cities:
		destinations.add(InlineKeyboardButton(text=city['city_name'],
		                                      callback_data=f'{city["destination_id"]}'))
	return destinations


def city(message, bot):
	bot.send_message(message.from_user.id, 'Уточните, пожалуйста:',
	                 reply_markup=city_markup(message.text))  # Отправляем кнопки с вариантами
