from telebot.types import Message

from config_data.config import DEFAULT_COMMANDS, BOT_COMMANDS
from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot_commands_text = ['/{command} - {desk}'.format(command=command, desk=desk) for command, desk in BOT_COMMANDS]
    bot.reply_to(message, 'Стандартные команды:\n' + '\n'.join(text) + '\n\nКоманды бота по поиску отелей:\n' + '\n'.join(bot_commands_text))
