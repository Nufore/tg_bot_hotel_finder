from config_data.config import LOG_PATH
from loguru import logger
from database.models import History

logger.add(LOG_PATH, format="{time} {level} {message}", level="ERROR", serialize=True)


@logger.catch()
def save_history_data(user_id: int, command: str, loc: str, hotels: list, date: str) -> None:
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


@logger.catch()
def get_history_data(user_id: int) -> list:
	history_list = [hist.hotels for hist in History.select().where(History.user_id == user_id)]
	return history_list
