from telebot.types import Message, CallbackQuery

from config_data.config import CUSTOM_COMMANDS
from keyboards.reply.bot_commands import bot_commands
from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    bot_commands_text = ['/{command} - {desk}'.format(command=command, desk=desk) for command, desk in CUSTOM_COMMANDS]
    # bot.reply_to(message, 'Команды бота по поиску отелей:\n' + '\n'.join(bot_commands_text))
    bot.send_message(message.from_user.id, 'Команды бота по поиску отелей:\n' + '\n'.join(bot_commands_text),
                     reply_markup=bot_commands())


@bot.callback_query_handler(func=lambda call: call.data == '/help')
def bot_help_callback(call: CallbackQuery):
    bot.answer_callback_query(call.id)
    bot_commands_text = ['/{command} - {desk}'.format(command=command, desk=desk) for command, desk in CUSTOM_COMMANDS]
    bot.send_message(call.message.chat.id, 'Команды бота по поиску отелей:\n' + '\n'.join(bot_commands_text),
                     reply_markup=bot_commands())
