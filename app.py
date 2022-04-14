from aiogram.utils import executor
from commands import set_default_commands
from handlers import dp


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
# venv\Scripts\activate.bat
# pip freeze > requirements.txt
