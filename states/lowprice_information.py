from telebot.handler_backends import State, StatesGroup

# 1. Город
# 2. Кол-во отелей
# 3. Вывод фото для каждого отеля
# 4. Кол-во фото


class UserInfoState(StatesGroup):
	checkin = State()
	checkout = State()
	sortOrder = State()
	city = State()
	number_of_hotels = State()
	is_need_photos = State()
	number_of_photos = State()
