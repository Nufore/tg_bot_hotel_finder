from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def min_max_price(is_min: bool = False, mltp: float = None) -> ReplyKeyboardMarkup:
	"""
	Функция создания reply-клавиатуры
	:return: Возвращает reply-клавиатуру с кнопками
	"""
	if is_min:
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		keyboard.row(KeyboardButton('10.0'), KeyboardButton('25.0'), KeyboardButton('50.0'))
		keyboard.row(KeyboardButton('100.0'), KeyboardButton('150.0'), KeyboardButton('200.0'))
		keyboard.row(KeyboardButton('300.0'), KeyboardButton('400.0'), KeyboardButton('500.0'))
		keyboard.row(KeyboardButton('750.0'), KeyboardButton('1000.0'))
		return keyboard
	else:
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		keyboard.row(KeyboardButton(str(mltp * 5)), KeyboardButton(str(mltp * 10)), KeyboardButton(str(mltp * 15)))
		keyboard.row(KeyboardButton(str(mltp * 20)), KeyboardButton(str(mltp * 25)), KeyboardButton(str(mltp * 30)))
		keyboard.row(KeyboardButton(str(mltp * 40)), KeyboardButton(str(mltp * 50)), KeyboardButton(str(mltp * 60)))
		keyboard.row(KeyboardButton(str(mltp * 75)), KeyboardButton(str(mltp * 100)))
		return keyboard
