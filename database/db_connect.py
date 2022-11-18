from config_data.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from peewee import *
from datetime import datetime


def save_history_data(user_id: int, command: str, loc: str, hotels: list, date: str) -> None:
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
	# db.execute_sql(f"insert into public.history"
	#                f"(user_id, command, date, hotels)"
	#                f"values"
	#                f"({user_id}, '{command}', '{datetime.now().replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')}',"
	#                f"'{'|'.join(hotels)}')")


def get_history_data(user_id: int) -> list:
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
