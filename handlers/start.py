from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from loader import dp


@dp.message_handler(CommandStart())
async def help_info(message: types.Message):
    await message.answer('Чтобы узнать функционал бота, пропишите комманду /help')