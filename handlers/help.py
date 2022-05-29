from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp
from loader import dp


@dp.message_handler(CommandHelp())
async def help_info(message: types.Message) -> None:
    await message.answer('Список команд:'
                         '\n/start - Запустить бота 💻'
                         '\n/help - Помощь ℹ️'
                         '\n/lowprice - вывод самых дешёвых отелей в городе 📉'
                         '\n/highprice - вывод самых дорогих отелей в городе 📈'
                         '\n/bestdeal - вывод отелей, наиболее подходящих по цене и расположению от центра 🔥'
                         '\n/history - вывод истории поиска отелей 📖'
                         )
