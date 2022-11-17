import json
import re
import requests
from typing import Any
from config_data.config import headers
from telebot.types import InputMediaPhoto


def str_bytes_check(entity: dict) -> str:
	"""
	Функция проверки длины строки для callback кнопок при выборе destination_id
	:param entity: Словарь из списка элементов entities в suggestions, где "group": "CITY_GROUP",
	полученный при запросе по url = "https://hotels4.p.rapidapi.com/locations/v2/search"
	:return: возвращает строку с названием локации
	"""
	str_c = re.sub("</span>", '', re.sub("<span class='highlighted'>", '', entity['caption']))
	if len(str_c.format('utf-8')) + len(entity['destinationId'].format('utf-8')) > 64:
		return entity.get('name', '???')
	else:
		return str_c


def ru_locale(s: str) -> bool:
	"""
	Функция проверки на наличие только русских букв в строке (также пробел и тире)
	:param s: строка для проверки
	:return: Возвращает True если все символы в строке - русские буквы, иначе False
	"""
	return bool(re.fullmatch(r'(?i)[а-яё -]+', s))


def get_text(data: dict) -> str:
	"""
	Функция формирования информации об отеле (подписи к фотографиям отеля)
	:param data: Словарь - элемент из списка results,
	полученный при запросе по url = "https://hotels4.p.rapidapi.com/properties/list"
	:return: Возвращает текст
	"""
	name = data["name"]
	postalCode = data["address"].get("postalCode", "No postalCode")
	countryName = data["address"]["countryName"]
	locality = data["address"]["locality"]
	streetAddress = data["address"].get("streetAddress", "No streetAddress")
	distance = data["landmarks"][0]["distance"]
	currentPrice = data["ratePlan"]["price"]["current"]
	fullyBundledPricePerStay = data["ratePlan"]["price"].get(
		"fullyBundledPricePerStay",
		"total ${cur}".format(cur=data["ratePlan"]["price"]["current"]))
	site_id = data["id"]
	text = f'<b>{name}</b>\n' \
	       f'{postalCode}, {countryName}, ' \
	       f'{locality}, {streetAddress}\n' \
	       f'Удаленность от центра: {distance}\n' \
	       f'Цена: {currentPrice} ' \
	       f'({fullyBundledPricePerStay})\n' \
	       f'https://www.hotels.com/ho{site_id}'.replace("&nbsp;", " ")
	return text


def get_request_data(
		message: str = None,
		locale: str = None,
		endpoint_id: str = None,
		number_of_photos: int = None,
		text: str = None,
		data: Any = None) -> list | None:
	"""
	Условие [message and locale] - поиск локаций для уточнения выбора пользователю
	:param message: Переданное название от пользователя при запросе указания города
	:param locale: Параметр языка для поиска ("ru_RU", "en_US")
	:return: Возвращает список словарей с нужным именем и id

	Условие [endpoint_id and number_of_photos and text] - поиск фотографий отеля (максимум 10 фото на каждый отель)
	:param endpoint_id: id отеля
	:param number_of_photos: Количество фото для вывода
	:param text: Текст с информацией об отеле
	:return: Возвращает список с элементами InputMediaPhoto для bot.send_media_group

	Условие [data] - поиск отелей по указанному городу/локации
	:param data: Список собранной информации от пользователя
	:return: Возвращает список results из searchResults
	при запросе по url = "https://hotels4.p.rapidapi.com/properties/list"
	"""
	if message and locale:
		url = "https://hotels4.p.rapidapi.com/locations/v2/search"

		querystring = {"query": message, "locale": locale}

		response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
		pattern = r'(?<="CITY_GROUP",).+?[\]]'

		if response.status_code == requests.codes.ok:
			find = re.search(pattern, response.text)
			if find:
				cities = list()
				suggestions = json.loads(f"{{{find[0]}}}")
				for dest_id in suggestions['entities']:  # Обрабатываем результат
					clear_destination = str_bytes_check(dest_id)
					cities.append({'city_name': clear_destination,
					               'destination_id': dest_id['destinationId']
					               }
					              )
				return cities
		else:
			print('timeout error')
			return

	elif endpoint_id and number_of_photos and text:
		if number_of_photos > 10:
			number_of_photos = 10
		url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

		querystring = {"id": endpoint_id}

		response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)

		if response.status_code == requests.codes.ok:
			pattern = r'(?<=,)"hotelImages":.+?(?=,"roomImages)'
			find = re.search(pattern, response.text)
			if find:
				result = json.loads(f"{{{find[0]}}}")
				media = list()
				for i_photo in range(number_of_photos):
					if media:
						media.append(InputMediaPhoto(result['hotelImages'][i_photo]['baseUrl'].replace('{size}', 'z')))
					else:
						media.append(InputMediaPhoto(result['hotelImages'][i_photo]['baseUrl'].replace('{size}', 'z'),
						                             caption=text, parse_mode='HTML'))
				return media
		else:
			print('timeout error')
			return

	elif data:
		if int(data['number_of_hotels']['data']) > 10:
			data['number_of_hotels']['data'] = '10'

		url = "https://hotels4.p.rapidapi.com/properties/list"

		if data.get("distance", None):
			querystring = {"destinationId": data['city'],
			               "pageNumber": "1",
			               "pageSize": "25",  # data['number_of_hotels']['data'],
			               "checkIn": data['checkin'],
			               "checkOut": data['checkout'],
			               "adults1": "1",
			               "priceMin": str(data['min_max_price']['minPrice']),
			               "priceMax": str(data['min_max_price']['maxPrice']),
			               "sortOrder": data['sortOrder'],
			               "landmarkIds": "City center"}
		else:
			querystring = {"destinationId": data['city'],
			               "pageNumber": "1",
			               "pageSize": data['number_of_hotels']['data'],
			               "checkIn": data['checkin'],
			               "checkOut": data['checkout'],
			               "adults1": "1",
			               "sortOrder": data['sortOrder']}

		response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)

		if response.status_code == requests.codes.ok:
			pattern = r'(?<=,)"results":.+?(?=,"pagination)'
			find = re.search(pattern, response.text)
			if find:
				result = json.loads(f"{{{find[0]}}}")
				return result['results']
		else:
			print('timeout error')
			return
