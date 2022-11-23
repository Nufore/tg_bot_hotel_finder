from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
	"""
	Класс состояний для сохранения информации вводимой пользователем

	checkin - Дата заезда

	checkout - Дата выезда

	sortOrder - Тип сортировки при поиске отеля
	[BEST_SELLER|STAR_RATING_HIGHEST_FIRST|STAR_RATING_LOWEST_FIRST|
	DISTANCE_FROM_LANDMARK|GUEST_RATING|PRICE_HIGHEST_FIRST|PRICE]

	city - Город для поиска. destination_id выбранный пользователем

	minMaxPrice - минимальная/максимальная цена для комманда /bestdeal

	distance - удаленность от центра для команды /bestdeal

	number_of_hotels - Количество выводимых отелей

	is_need_photos - Параметр вывода фото. Если да, то выводим

	number_of_photos - Количество выводимых фото
	"""
	checkin = State()
	checkout = State()
	sortOrder = State()
	city = State()
	minMaxPrice = State()
	distance = State()
	number_of_hotels = State()
	is_need_photos = State()
	number_of_photos = State()
