from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def bot_commands() -> ReplyKeyboardMarkup:
	"""
	Функция создания reply-клавиатуры с основными командами бота
	:return: Возвращает reply-клавиатуру
	"""
	lowprice_btn = KeyboardButton('/lowprice')
	highprice_btn = KeyboardButton('/highprice')
	bestdeal_btn = KeyboardButton('/bestdeal')
	history_btn = KeyboardButton('/history')
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

	keyboard.row(lowprice_btn, highprice_btn)
	keyboard.row(bestdeal_btn, history_btn)
	return keyboard
