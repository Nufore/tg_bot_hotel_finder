from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def inline_help() -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup()
	key_1 = InlineKeyboardButton(text="❔HELP❔", callback_data="/help")
	keyboard.add(key_1)
	return keyboard
