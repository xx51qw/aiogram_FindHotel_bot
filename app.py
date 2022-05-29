from aiogram.utils import executor
from loguru import logger

from commands import set_default_commands
from db_api import db_gino
from db_api.db_gino import db
from handlers import dp


logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="1 week",
           compression="zip")


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)

    logger.info('Подключаем БД')
    await db_gino.on_startup(dispatcher)

    logger.info('Чистим базу')
    await db.gino.drop_all()

    logger.info('Создаем таблицы')
    await db.gino.create_all()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
# venv\Scripts\activate.bat
# pip freeze > requirements.txt
