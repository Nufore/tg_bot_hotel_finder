import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
NO_PHOTO = os.getenv('NO_PHOTO_PATH')

LOG_PATH = os.getenv('LOG_PATH')

headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку")
)
CUSTOM_COMMANDS = (
    ('lowprice', "Топ самых дешёвых отелей"),
    ('highprice', "Топ самых дорогих отелей"),
    ('bestdeal', "Топ отелей, наиболее подходящих по цене и расположению от центра"
                 "(самые дешёвые и находятся ближе всего к центру)"),
    ('history', "История поиска отелей")
)

LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}

#  Подключение к БД
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
