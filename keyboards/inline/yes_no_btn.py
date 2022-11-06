from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def yes_no() -> InlineKeyboardMarkup:
	"""
	Функция создания inline-клавиатуры
	:return: Возвращает inline-клавиатуру с кнопками
	"""
	keyboard = InlineKeyboardMarkup()
	key_1 = InlineKeyboardButton(text="Да", callback_data="Да")
	key_2 = InlineKeyboardButton(text="Нет", callback_data="Нет")
	keyboard.row(key_1, key_2)
	return keyboard
