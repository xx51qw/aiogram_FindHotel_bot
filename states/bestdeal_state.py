from aiogram.dispatcher.filters.state import StatesGroup, State


class Bestdeal(StatesGroup):
    time = State()
    city = State()
    id_city = State()
    price = State()
    distance = State()
    arrival_date = State()
    departure_date = State()
    quantity_hotels = State()
    photo = State()
