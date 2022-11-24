import peewee

from config_data.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, LOG_PATH
from peewee import *
from loguru import logger

logger.add(LOG_PATH, format="{time} {level} {message}", level="ERROR", serialize=True)


@logger.catch()
def save_history_data(user_id: int, command: str, loc: str, hotels: list, date: str) -> None:
	try:
		db = PostgresqlDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

		class History(Model):
			user_id = IntegerField()
			command = CharField()
			date = CharField()
			hotels = TextField()

			class Meta:
				database = db

		if command == 'PRICE':
			command = '/lowprice'
		elif command == 'PRICE_HIGHEST_FIRST':
			command = '/highprice'
		elif command == 'DISTANCE_FROM_LANDMARK':
			command = '/bestdeal'

		text = command + '\n' + loc + '\n' + date + '\n' + '\n'.join(hotels)

		History.create(user_id=user_id,
		               command=command,
		               date=date,
		               hotels=text)
	except peewee.OperationalError:
		logger.error("Ошибка подключения к БД. Проверьте данные подключения.")


@logger.catch()
def get_history_data(user_id: int) -> list:
	try:
		db = PostgresqlDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

		class History(Model):
			user_id = IntegerField()
			command = CharField()
			date = CharField()
			hotels = TextField()

			class Meta:
				database = db

		history_list = [hist.hotels for hist in History.select().where(History.user_id == user_id)]
		return history_list
	except peewee.OperationalError:
		logger.error("Ошибка подключения к БД. Проверьте данные подключения.")
		return False
