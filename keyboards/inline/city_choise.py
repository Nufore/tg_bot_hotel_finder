import datetime
import json
import re
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

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

	find = re.search(pattern, response.text)
	if find:
		cities = list()
		suggestions = json.loads(f"{{{find[0]}}}")
		for dest_id in suggestions['entities']:  # Обрабатываем результат
			clear_destination = re.sub("</span>", '', re.sub("<span class='highlighted'>", '', dest_id['caption']))
			cities.append({'city_name': clear_destination,
			               'destination_id': dest_id['destinationId']
			               }
			              )
		return cities
	return


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


def get_photos(endpoint_id, number_of_photos):
	if number_of_photos > 10:
		number_of_photos = 10
	url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

	querystring = {"id": endpoint_id}

	headers = {
		"X-RapidAPI-Key": config.RAPID_API_KEY,
		"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
	}

	response = requests.request("GET", url, headers=headers, params=querystring)

	if response.status_code == requests.codes.ok:
		pattern = r'(?<=,)"hotelImages":.+?(?=,"roomImages)'
		find = re.search(pattern, response.text)
		if find:
			result = json.loads(f"{{{find[0]}}}")
			media = list()
			for i_photo in range(number_of_photos):
				media.append(InputMediaPhoto(
					result['hotelImages'][i_photo]['baseUrl'].replace('{size}', 'z')
				))
			return media
	else:
		print('timeout error')


def hotel_founding(data):
	max_number = 10
	if int(data['number_of_hotels']) > max_number:
		data['number_of_hotels'] = str(max_number)

	url = "https://hotels4.p.rapidapi.com/properties/list"

	querystring = {"destinationId": data['city'], "pageNumber": "1", "pageSize": data['number_of_hotels'],
	               "checkIn": datetime.date.today(),
	               "checkOut": datetime.date.today() + datetime.timedelta(days=1),
	               "adults1": "1", "sortOrder": "PRICE"}

	headers = {
		"X-RapidAPI-Key": config.RAPID_API_KEY,
		"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
	}

	response = requests.request("GET", url, headers=headers, params=querystring)

	if response.status_code == requests.codes.ok:
		pattern = r'(?<=,)"results":.+?(?=,"pagination)'
		find = re.search(pattern, response.text)
		if find:
			result = json.loads(f"{{{find[0]}}}")
			if data['is_need_photos'] == 'Да':
				return result['results']
	else:
		print('timeout error')
