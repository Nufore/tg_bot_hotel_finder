from peewee import Model, IntegerField, CharField, TextField, PostgresqlDatabase, OperationalError
from config_data.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from loguru import logger

try:
	db = PostgresqlDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
except OperationalError:
	logger.error("Ошибка подключения к БД. Проверьте данные подключения.")


class History(Model):
	user_id = IntegerField()
	command = CharField()
	date = CharField()
	hotels = TextField()

	class Meta:
		database = db
