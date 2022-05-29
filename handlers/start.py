from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from db_api import sql_commands as command
from loader import dp


@dp.message_handler(CommandStart())
async def help_info(message: types.Message) -> None:
    name = message.from_user.full_name
    await message.answer('Чтобы узнать функционал бота, пропишите команду /help')
    await command.add_user(id=message.from_user.id, name=name)
