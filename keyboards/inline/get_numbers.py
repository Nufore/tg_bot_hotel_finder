from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_number() -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup()
	key_1 = InlineKeyboardButton(text="1", callback_data="1")
	key_2 = InlineKeyboardButton(text="2", callback_data="2")
	key_3 = InlineKeyboardButton(text="3", callback_data="3")
	key_4 = InlineKeyboardButton(text="4", callback_data="4")
	key_5 = InlineKeyboardButton(text="5", callback_data="5")
	key_6 = InlineKeyboardButton(text="6", callback_data="6")
	key_7 = InlineKeyboardButton(text="7", callback_data="7")
	key_8 = InlineKeyboardButton(text="8", callback_data="8")
	key_9 = InlineKeyboardButton(text="9", callback_data="9")
	key_10 = InlineKeyboardButton(text="10", callback_data="10")
	keyboard.add(key_1, key_2, key_3, key_4, key_5, key_6, key_7, key_8, key_9, key_10)
	return keyboard
