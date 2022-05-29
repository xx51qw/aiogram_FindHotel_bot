from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from Calendar import simple_cal_callback
from pagination.callback_datas import photo_callback
from loader import dp
from parse import bestdeal
from states import Bestdeal
from utils import best_deal


@dp.message_handler(Command('bestdeal'))
async def city_name(message: Message, state: FSMContext) -> None:
    await best_deal.get_city_name(message, state=state, cmd=bestdeal, current_state=Bestdeal)


@dp.message_handler(state=Bestdeal.city)
async def select_city(message: Message, state: FSMContext) -> None:
    await best_deal.show_city_list(message, state, current_state=Bestdeal)


@dp.callback_query_handler(state=Bestdeal.id_city)
async def arrival_date(callback: CallbackQuery, state: FSMContext) -> None:
    await best_deal.get_entry_date(callback, state, current_state=Bestdeal)


@dp.message_handler(state=Bestdeal.price)
async def choose_price(message: Message, state: FSMContext) -> None:
    await best_deal.price_range(message, state, current_state=Bestdeal)


@dp.message_handler(state=Bestdeal.distance)
async def choose_distance(message: Message, state: FSMContext) -> None:
    await best_deal.range_of_distances(message, state, current_state=Bestdeal)


@dp.callback_query_handler(simple_cal_callback.filter(), state=Bestdeal.arrival_date)
async def departure_date(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:
    await best_deal.get_departure_date(callback, callback_data, state, current_state=Bestdeal)


@dp.callback_query_handler(simple_cal_callback.filter(), state=Bestdeal.departure_date)
async def quantity_hotels(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:
    await best_deal.ask_about_hotel_quantity(callback, callback_data, state, current_state=Bestdeal)


@dp.message_handler(state=Bestdeal.quantity_hotels)
async def need_photo(message: Message, state: FSMContext) -> None:
    await best_deal.ask_of_photo(message, state, current_state=Bestdeal)


@dp.callback_query_handler(lambda call: call.data == 'Нет', state=Bestdeal.photo)
async def result(callback: CallbackQuery, state: FSMContext) -> None:
    await best_deal.send_result_without_photo(callback, state, cmd=bestdeal)


@dp.callback_query_handler(lambda call: call.data == 'Да', state=Bestdeal.photo)
async def send_hotels_with_photo(callback: CallbackQuery, state: FSMContext) -> None:
    await best_deal.send_result_with_photo(callback, state, cmd=bestdeal)


@dp.callback_query_handler(photo_callback.filter(), state='*')
async def photo_page_handler(query: CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await best_deal.scroll_photo(query, callback_data, state)
