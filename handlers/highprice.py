from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from parse import highprice
from utils import common
from Calendar import simple_cal_callback
from loader import dp
from pagination.callback_datas import photo_callback
from states import HighPrice


@dp.message_handler(Command('highprice'))
async def city_name(message: Message, state: FSMContext) -> None:
    await common.get_city_name(message, state=state, cmd=highprice, current_state=HighPrice)


@dp.message_handler(state=HighPrice.city)
async def select_city(message: Message, state: FSMContext) -> None:
    await common.show_city_list(message, state, current_state=HighPrice)


@dp.callback_query_handler(state=HighPrice.id_city)
async def arrival_date(callback: CallbackQuery, state: FSMContext) -> None:
    await common.get_entry_date(callback, state, current_state=HighPrice)


@dp.callback_query_handler(simple_cal_callback.filter(), state=HighPrice.arrival_date)
async def departure_date(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:
    await common.get_departure_date(callback_query, callback_data, state, current_state=HighPrice)


@dp.callback_query_handler(simple_cal_callback.filter(), state=HighPrice.departure_date)
async def quantity_hotels(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:
    await common.ask_about_hotel_quantity(callback_query, callback_data, state, current_state=HighPrice)


@dp.message_handler(state=HighPrice.quantity_hotels)
async def ask_of_photo(message: Message, state: FSMContext) -> None:
    await common.ask_of_photo(message, state, current_state=HighPrice)


@dp.callback_query_handler(lambda call: call.data == 'Нет', state=HighPrice.photo)
async def result(callback: CallbackQuery, state: FSMContext) -> None:
    await common.send_result_without_photo(callback, state, cmd=highprice)


@dp.callback_query_handler(lambda call: call.data == 'Да', state=HighPrice.photo)
async def send_hotels_with_photo(callback: CallbackQuery, state: FSMContext) -> None:
    await common.send_result_with_photo(callback, state, cmd=highprice)


@dp.callback_query_handler(photo_callback.filter(), state='*')
async def photo_page_handler(query: CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await common.scroll_photo(query, callback_data, state)
