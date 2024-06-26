from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def request_photo() -> ReplyKeyboardMarkup:
	"""
	Функция создания reply-клавиатуры
	:return: Возвращает reply-клавиатуру с кнопками
	"""
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	keyboard.row(KeyboardButton('Да'), KeyboardButton('Нет'))
	return keyboard
