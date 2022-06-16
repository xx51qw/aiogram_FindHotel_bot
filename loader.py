from aiogram import Bot, Dispatcher, types
from decouple import config
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(config('TOKEN_BOT'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

PGUSER = config('PGUSER')
PGPASSWORD = config('PGPASSWORD')
DATABASE = config('DATABASE')
ip = '127.0.0.1'
POSTGRES_URI = f'postgresql://{PGUSER}:{PGPASSWORD}@{ip}/{DATABASE}'

headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': config('HOTELS_API')
    }
