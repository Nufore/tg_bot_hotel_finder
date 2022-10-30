import json
import re
import requests
import types
from config_data import config
from telebot.types import InputMediaPhoto


def str_bytes_check(entity: dict):
	str_c = re.sub("</span>", '', re.sub("<span class='highlighted'>", '', entity['caption']))
	if len(str_c.format('utf-8')) + len(entity['destinationId'].format('utf-8')) > 64:
		return entity.get('name', '???')
	else:
		return str_c

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
			clear_destination = str_bytes_check(dest_id)
			cities.append({'city_name': clear_destination,
			               'destination_id': dest_id['destinationId']
			               }
			              )
		return cities
	return


def get_photos(endpoint_id, number_of_photos, text):
	if number_of_photos > 10:
		number_of_photos = 10
	url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

	querystring = {"id": endpoint_id}

	headers = {
		"X-RapidAPI-Key": config.RAPID_API_KEY,
		"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
	}

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
					media.append(
						InputMediaPhoto(result['hotelImages'][i_photo]['baseUrl'].replace('{size}', 'z'),
						                caption=text, parse_mode='HTML')
					)
			return media
	else:
		print('timeout error')
		return


def hotel_founding(data):
	max_number = 10
	if int(data['number_of_hotels']) > max_number:
		data['number_of_hotels'] = str(max_number)

	url = "https://hotels4.p.rapidapi.com/properties/list"

	querystring = {"destinationId": data['city'], "pageNumber": "1", "pageSize": data['number_of_hotels'],
	               "checkIn": data['checkin'],
	               "checkOut": data['checkout'],
	               "adults1": "1", "sortOrder": data['sortOrder']}

	headers = {
		"X-RapidAPI-Key": config.RAPID_API_KEY,
		"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
	}

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


def get_text(data, str_type):
	if str_type == 'output_data':
		text = f'<b>{data["name"]}</b>\n' \
		       f'{data["address"].get("postalCode", "No postalCode")}, {data["address"]["countryName"]}, ' \
		       f'{data["address"]["locality"]}, {data["address"].get("streetAddress","No streetAddress")}\n' \
		       f'Удаленность от центра: {data["landmarks"][0]["distance"]}\n' \
		       f'Цена: {data["ratePlan"]["price"]["current"]} ' \
		       f'({data["ratePlan"]["price"].get("fullyBundledPricePerStay", "total ${cur}".format(cur=data["ratePlan"]["price"]["current"]))})\n' \
			   f'https://www.hotels.com/ho{data["id"]}'.replace("&nbsp;", " ")
		return text
	elif str_type == 'collected_data_1':
		text = f'Собранная информация: \n' \
		       f'Город - {data["city"]}\nКол-во отелей - {data["number_of_hotels"]}\n' \
		       f'Нужны ли фото - {data["is_need_photos"]}\nКол-во фото - {data["number_of_photos"]}'
		return text
	elif str_type == 'collected_data_2':
		text = f'Собранная информация: \n' \
		       f'Город - {data["city"]}\nКол-во отелей - {data["number_of_hotels"]}\n' \
		       f'Нужны ли фото - {data["is_need_photos"]}'
		return text