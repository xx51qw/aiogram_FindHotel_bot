from aiogram.dispatcher.filters.state import StatesGroup, State


class LowPrice(StatesGroup):
    city = State()
    id_city = State()
    arrival_date = State()
    departure_date = State()
    quantity_hotels = State()
    photo = State()
    days_quantity = State()
    hotels = State()
    hotel_id = State()
    images = State()
