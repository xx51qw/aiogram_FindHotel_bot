import re
from datetime import datetime, timedelta
from json import JSONDecodeError

from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMedia
from aiogram.utils.callback_data import CallbackData
from aiogram_calendar import simple_cal_callback, SimpleCalendar

from pagination.callback_datas import photo_callback
from pagination.inline_photo import get_photo_keyboard
from loader import dp, bot
from parse import get_city, lowprice, get_photo
from states import LowPrice


@dp.message_handler(Command('lowprice'))
async def city_name(message: Message):
    await message.answer('Введите город: ')
    await LowPrice.city.set()


@dp.message_handler(state=LowPrice.city)
async def select_city(message: Message, state: FSMContext):
    if re.search(r'\d', message.text) is None:
        if re.search(r'[@.,:;^№!?_*+()/#¤%&]', message.text) is None:
            await state.update_data(city=message.text)
            city = await get_city(message.text)
            keyboard = InlineKeyboardMarkup(row_width=1)
            for elem in city:
                keyboard.add(InlineKeyboardButton(text=elem, callback_data=city.get(elem)))
            await message.answer('Выберите подходящий город из списка: ', reply_markup=keyboard)
            await LowPrice.id_city.set()

        else:
            await message.answer('Ошибка ввода! ⛔ \nГород содержит специальные символы, попробуйте снова')
            await LowPrice.city.set()

    else:
        await message.answer('Ошибка ввода! ⛔ \nГород содержит цифры, попробуйте снова')
        LowPrice.city.set()


@dp.callback_query_handler(state=LowPrice.id_city)
async def arrival_date(callback: CallbackQuery, state: FSMContext):
    id_city = callback.data
    await callback.answer()
    await state.update_data(id_city=id_city)
    await callback.message.delete_reply_markup()
    await callback.message.answer("Заезд: ", reply_markup=await SimpleCalendar().start_calendar())
    await LowPrice.arrival_date.set()


@dp.callback_query_handler(simple_cal_callback.filter(), state=LowPrice.arrival_date)
async def departure_date(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)

    if selected:
        dt_now = datetime.now()
        if datetime.strptime(date.strftime("%Y%m%d"), "%Y%m%d").date() >= dt_now.date():
            await callback_query.message.delete_reply_markup()
            await callback_query.message.answer(f'Дата заезда {date.strftime("%d/%m/%Y")}')
            await state.update_data(arrival_date=datetime.strptime(date.strftime("%Y%m%d"), "%Y%m%d").date())
            await callback_query.message.answer("Выезд: ",
                                                reply_markup=await SimpleCalendar().start_calendar())
            await LowPrice.departure_date.set()

        else:
            await callback_query.answer(f'Невозможно забронировать отель раньше {dt_now.date().strftime("%d/%m/%Y")}')
            await LowPrice.arrival_date.set()


@dp.callback_query_handler(simple_cal_callback.filter(), state=LowPrice.departure_date)
async def quantity_hotels(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)

    if selected:
        get_data = await state.get_data()
        if get_data.get('arrival_date') < datetime.strptime(date.strftime("%Y%m%d"), "%Y%m%d").date():
            await callback_query.message.delete_reply_markup()
            await callback_query.message.answer(f'Дата выезда {date.strftime("%d/%m/%Y")}')
            await state.update_data(departure_date=datetime.strptime(date.strftime("%Y%m%d"), "%Y%m%d").date())
            await callback_query.message.answer('Введите количество отелей (от 1 до 25): ')
            await LowPrice.quantity_hotels.set()

        else:
            correct_arrival_date = get_data.get("arrival_date") + timedelta(days=1)
            await callback_query.answer(f'Дата выезда не может быть раньше {correct_arrival_date.strftime("%d/%m/%Y")}')
            await LowPrice.departure_date.set()


@dp.message_handler(state=LowPrice.quantity_hotels)
async def need_photo(message: Message, state: FSMContext):
    number_of_hotels = message.text
    if re.search(r'\D', number_of_hotels):
        await message.answer('Ошибка ввода! ⛔ \nМожно вводить только цифры, попробуйте снова')
        await LowPrice.quantity_hotels.set()
    elif 1 <= int(number_of_hotels) <= 25:
        number_of_hotels = message.text
        await state.update_data(quantity_hotels=number_of_hotels)
        choice = InlineKeyboardMarkup(row_width=2)
        choice.row(InlineKeyboardButton(text='Да ✅', callback_data='Да'))
        choice.row(InlineKeyboardButton(text='Нет ❌', callback_data='Нет'))
        await message.answer('Показать фото отелей?', reply_markup=choice)
        await LowPrice.photo.set()
    else:
        await message.answer('Ошибка ввода! ⛔ \nНужно ввести число от 1 до 25, попробуйте снова')
        await LowPrice.quantity_hotels.set()


@dp.callback_query_handler(lambda call: call.data == 'Нет', state=LowPrice.photo)
async def result(callback: CallbackQuery, state: FSMContext):
    photo = callback.data
    await state.update_data(photo=photo)
    data = await state.get_data()
    await callback.message.delete_reply_markup()
    print(data)
    id_city = data.get('id_city')
    days_quantity = (data['departure_date'] - data['arrival_date']).days
    hotels = await lowprice(data, id_city, days_quantity)
    await callback.message.answer('Приступаю к поиску 🔎')
    try:
        for hotel in hotels:
            await state.update_data(days_quantity=days_quantity,
                                    hotels=hotels,
                                    )
            await callback.message.answer(f'Название отеля {hotel[1]}\n'
                                          f'\nАдрес: {hotel[2]}'
                                          f'\nРасстояние до центра города: {hotel[3]}'
                                          f'\nРейтинг отеля: {hotel[4]} ⭐️'
                                          f'\nЦена за ночь: {hotel[5]} ₽'
                                          f'\nЦена за весь период: {hotel[6]} ₽'
                                          f'\nСсылка на номер: {hotel[7]}')

        await state.reset_state()
        await callback.message.answer('Команда выполнена. Для просмотра всего функционала введите /help')

    except JSONDecodeError:
        await callback.message.answer('Не получилось найти данные по введенному городу, попробуйте снова.\n'
                                      'Для этого пропишите команду /lowprice')
        await state.reset_state()
    except TypeError:
        await callback.message.answer('В ходе поиска возникла ошибка, попробуйте снова.\n'
                                      'Для этого пропишите команду /lowprice')
        await state.reset_state()


@dp.callback_query_handler(lambda call: call.data == 'Да', state=LowPrice.photo)
async def send_hotels_with_photo(callback: CallbackQuery, state: FSMContext):
    photo = callback.data
    await state.update_data(photo=photo)
    try:
        data = await state.get_data()
        await callback.message.answer('Приступаю к поиску 🔎')
        await callback.message.delete_reply_markup()
        id_city = data.get('id_city')
        days_quantity = (data['departure_date'] - data['arrival_date']).days
        hotels = await lowprice(data, id_city, days_quantity)
        for hotel in hotels:
            photo_dict = await get_photo(hotel[0])
            await state.update_data(days_quantity=days_quantity,
                                    hotels=hotels,
                                    images=photo_dict)
            photo_data = photo_dict[0]
            photo_keyboard = get_photo_keyboard(photo_dict)  # Page: 0
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=photo_data.get("image_url"),
                parse_mode="HTML",
                reply_markup=photo_keyboard
            )

            await callback.message.answer(f'Название отеля: {hotel[1]}'
                                          f'\nАдрес: {hotel[2]}'
                                          f'\nРасстояние до центра города: {hotel[3]}'
                                          f'\nРейтинг отеля: {hotel[4]} ⭐️'
                                          f'\nЦена за ночь: {hotel[5]} ₽'
                                          f'\nЦена за весь период: {hotel[6]} ₽'
                                          f'\nСсылка на номер: {hotel[7]}')
    except JSONDecodeError:
        await callback.message.answer('Не получилось найти данные по введенному городу, попробуйте снова.\n'
                                      'Для этого пропишите команду /lowprice')
        await state.finish()
    except TypeError:
        await callback.message.answer('В ходе поиска возникла ошибка, попробуйте снова.\n'
                                      'Для этого пропишите команду /lowprice')
        await state.finish()


@dp.callback_query_handler(photo_callback.filter(), state='*')
async def photo_page_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    data = await state.get_data()
    photo_dict = data.get('images')
    page = int(callback_data.get("page"))
    photo_data = photo_dict[page]
    keyboard = get_photo_keyboard(photo_dict, page)

    photo = InputMedia(type="photo", media=photo_data.get("image_url"))

    await query.message.edit_media(photo, keyboard)
    await state.reset_state(with_data=False)
