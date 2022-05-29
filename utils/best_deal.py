import re
from datetime import datetime, timedelta
from json import JSONDecodeError
from loguru import logger
from typing import Callable
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMedia
from aiogram.utils.callback_data import CallbackData
from Calendar import SimpleCalendar
from images import Images

from pagination.inline_photo import get_photo_keyboard
from loader import bot
from parse import get_city, get_photo
from states import Bestdeal
from db_api import sql_commands as command


@logger.catch
async def get_city_name(message: Message, state: FSMContext, cmd: Callable, current_state) -> None:
    logger.info(f'Пользователь с id: {message.from_user.id} запустил команду /{cmd.__name__}')
    time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    await state.update_data(time=time)
    await message.answer('Введите город: ')
    await current_state.city.set()


@logger.catch
async def show_city_list(message: Message, state: FSMContext, current_state) -> None:
    if re.search(r'\d', message.text) is None:
        if re.search(r'[@.,:;^№!?_*+()/#¤%&]', message.text) is None:
            await state.update_data(city=message.text)
            city = await get_city(message.text)
            if city:
                keyboard = InlineKeyboardMarkup(row_width=1)
                for elem in city:
                    keyboard.add(InlineKeyboardButton(text=elem, callback_data=city.get(elem)))
                await message.answer('Выберите подходящий город из списка: ', reply_markup=keyboard)
                await current_state.id_city.set()
            else:
                await message.answer('Не удалось найти город с таким названием, попробуйте снова')
                await current_state.city.set()

        else:
            await message.answer('Ошибка ввода! ⛔ \nГород содержит специальные символы, попробуйте снова')
            await Bestdeal.city.set()

    else:
        await message.answer('Ошибка ввода! ⛔ \nГород содержит цифры, попробуйте снова')
        Bestdeal.city.set()


@logger.catch
async def get_entry_date(callback: CallbackQuery, state: FSMContext, current_state) -> None:
    id_city = callback.data
    data = await state.get_data()
    city = await get_city(data.get('city'))
    for key, value in city.items():
        if value == id_city:
            name = key
            logger.info(f'Пользователь  c id {callback.from_user.id} выбрал город {name}')
            await callback.message.answer(name)
    await callback.answer()
    await state.update_data(id_city=id_city)
    await callback.message.delete_reply_markup()
    await callback.message.answer('Введите диапазон цен в рублях за ночь через пробел, пример: 3000 5000')
    await current_state.price.set()


@logger.catch
async def price_range(message: Message, state: FSMContext, current_state) -> None:
    price = message.text
    list_of_prices = price.split()
    if len(list_of_prices) == 2:
        if list_of_prices[0].isdigit() and list_of_prices[1].isdigit():
            start_price = int(list_of_prices[0])
            finish_price = int(list_of_prices[1])
            if start_price > finish_price:
                await message.answer('Ошибка ввода! ⛔ \nСтартовая цена не может быть больше конечной, '
                                     'попробуйте снова')
                await current_state.price.set()

            elif start_price == finish_price:
                await message.answer('Ошибка ввода! ⛔ \nВведенные цены не могут быть одинаковыми, '
                                     'попробуйте снова')

            else:
                await state.update_data(start_price=start_price, finish_price=finish_price)
                logger.info(f'Пользователь  c id {message.from_user.id} '
                            f'выбрал стоимость от {start_price} до {finish_price}')
                await message.answer('Введите диапазон расстояния отеля от центра города в км, пример: 0.3 1.5')
                await current_state.distance.set()

        else:
            await message.answer('Ошибка ввода! ⛔ \nВводить можно только цифры, попробуйте снова')
            await current_state.price.set()

    else:
        await message.answer('Ошибка ввода! ⛔ \nНужно ввести два значения, попробуйте снова')
        await current_state.price.set()


@logger.catch
async def range_of_distances(message: Message, state: FSMContext, current_state) -> None:
    answer = message.text
    list_of_distances = answer.split()
    if len(list_of_distances) == 2:
        start_distance = list_of_distances[0]
        finish_distance = list_of_distances[1]
        if start_distance.isdigit() or finish_distance.isdigit() or re.findall(r"\d*\.\d+", start_distance) \
                or re.findall(r"\d*\.\d+", finish_distance):
            if float(start_distance) > float(finish_distance):
                await message.answer('Ошибка ввода! ⛔ \nПервое число не может быть больше второго, '
                                     'попробуйте снова')
                await current_state.distance.set()
            else:
                logger.info(f'Пользователь  c id {message.from_user.id} '
                            f'выбрал расстояние до центра  от {start_distance}км до {finish_distance}км')
                await state.update_data(start_distance=start_distance, finish_distance=finish_distance)
                await message.answer("Заезд: ", reply_markup=await SimpleCalendar().start_calendar())
                await current_state.arrival_date.set()
        else:
            await message.answer('Ошибка ввода! ⛔ \nВведенные данные не являются числом, попробуйте снова')
            await current_state.distance.set()
    else:
        await message.answer('Ошибка ввода! ⛔ \nНужно ввести два значения, попробуйте снова')
        await current_state.distance.set()


@logger.catch
async def get_departure_date(callback: CallbackQuery, callback_data: CallbackData,
                             state: FSMContext, current_state) -> None:
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        dt_now = datetime.now()
        if datetime.strptime(date.strftime("%Y%m%d"), "%Y%m%d").date() >= dt_now.date():
            await callback.message.delete_reply_markup()
            await callback.message.answer(f'Дата заезда {date.strftime("%d/%m/%Y")}')
            await state.update_data(arrival_date=datetime.strptime(date.strftime("%Y%m%d"), "%Y%m%d").date())
            await callback.message.answer("Выезд: ",
                                          reply_markup=await SimpleCalendar().start_calendar())
            logger.info(f'Пользователь  c id {callback.from_user.id} выбрал заезд {date.strftime("%d/%m/%Y")}')
            await current_state.departure_date.set()

        else:
            await callback.answer(f'Невозможно забронировать отель раньше {dt_now.date().strftime("%d/%m/%Y")}')
            await current_state.arrival_date.set()


@logger.catch
async def ask_about_hotel_quantity(callback: CallbackQuery, callback_data: CallbackData,
                                   state: FSMContext, current_state) -> None:
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        get_data = await state.get_data()
        if get_data.get('arrival_date') < datetime.strptime(date.strftime("%Y%m%d"), "%Y%m%d").date():
            await callback.message.delete_reply_markup()
            await callback.message.answer(f'Дата выезда {date.strftime("%d/%m/%Y")}')
            await state.update_data(departure_date=datetime.strptime(date.strftime("%Y%m%d"), "%Y%m%d").date())
            await callback.message.answer('Введите количество отелей (от 1 до 25): ')
            logger.info(f'Пользователь  c id {callback.from_user.id} выбрал выезд {date.strftime("%d/%m/%Y")}')
            await current_state.quantity_hotels.set()

        else:
            correct_arrival_date = get_data.get("arrival_date") + timedelta(days=1)
            await callback.answer(f'Дата выезда не может быть раньше {correct_arrival_date.strftime("%d/%m/%Y")}')
            await current_state.departure_date.set()


@logger.catch
async def ask_of_photo(message: Message, state: FSMContext, current_state) -> None:
    number_of_hotels = message.text
    if re.search(r'\D', number_of_hotels):
        await message.answer('Ошибка ввода! ⛔ \nМожно вводить только цифры, попробуйте снова')
        await current_state.quantity_hotels.set()

    elif 1 <= int(number_of_hotels) <= 25:
        number_of_hotels = message.text
        await state.update_data(quantity_hotels=number_of_hotels)
        logger.info(f'Пользователь  c id {message.from_user.id} '
                    f'указал количество отелей: {number_of_hotels}')
        choice = InlineKeyboardMarkup(row_width=2)
        choice.row(InlineKeyboardButton(text='Да ✅', callback_data='Да'))
        choice.row(InlineKeyboardButton(text='Нет ❌', callback_data='Нет'))
        await message.answer('Показать фото отелей?', reply_markup=choice)
        await current_state.photo.set()

    else:
        await message.answer('Ошибка ввода! ⛔ \nНужно ввести число от 1 до 25, попробуйте снова')
        await current_state.quantity_hotels.set()


@logger.catch
async def send_result_without_photo(callback: CallbackQuery, state: FSMContext, cmd: Callable) -> None:
    photo = callback.data
    logger.info(f'Пользователь  c id {callback.from_user.id} выбрал вывод отелей без фото')
    await callback.message.answer(photo)
    await state.update_data(photo=photo)
    try:
        await callback.message.answer('Приступаю к поиску 🔎')
        logger.info(f"Бот приступает к выполнению команды /{cmd.__name__}")
        data = await state.get_data()
        await callback.message.delete_reply_markup()
        id_city = data.get('id_city')
        days_quantity = (data['departure_date'] - data['arrival_date']).days
        quantity_hotels = data.get('quantity_hotels')
        time = data.get('time')
        hotels = await cmd(data, id_city, days_quantity)

        if hotels:
            if len(hotels) < int(quantity_hotels):
                await callback.message.answer(f'По указанным параметрам удалось найти отелей: {len(hotels)}')
            for i_hotel in hotels:
                hotel_name = i_hotel[1]
                hotel_address = i_hotel[2]
                distance_to_center = i_hotel[3]
                rating = i_hotel[4]
                one_night_price = i_hotel[5]
                full_price = i_hotel[6]
                hotel_link = i_hotel[7]
                await command.add_hotel(command=cmd.__name__, time=time, id=callback.from_user.id, name=hotel_name,
                                        address=hotel_address,
                                        rating=rating, distance=distance_to_center, night_price=one_night_price,
                                        all_period_price=full_price, link=hotel_link)
                await callback.message.answer(f'Название отеля {hotel_name}\n'
                                              f'\nАдрес: {hotel_address}'
                                              f'\nРасстояние до центра города: {distance_to_center}'
                                              f'\nРейтинг отеля: {rating} ⭐️'
                                              f'\nЦена за ночь: {one_night_price} ₽'
                                              f'\nЦена за весь период: {full_price} ₽'
                                              f'\nСсылка на номер: {hotel_link}')

            await state.reset_state()
            await callback.message.answer('Команда выполнена. Для просмотра всего функционала введите /help')
        else:
            await callback.message.answer('К сожалению по вашему запросу ничего не найдено. Попробуйте изменить '
                                          'критерии поиска и попробовать снова. Для этого введите команду '
                                          f'/{cmd.__name__}')
            await state.reset_state()

    except JSONDecodeError:
        logger.error("Ошибка JSONDecodeError")
        await callback.message.answer('Не получилось найти данные по введенному городу, попробуйте снова.\n'
                                      f'Для этого пропишите команду /{cmd.__name__}')
        await state.reset_state()

    except TypeError:
        logger.error("Ошибка TypeError")
        await callback.message.answer('В ходе поиска возникла ошибка, попробуйте снова.\n'
                                      f'Для этого пропишите команду /{cmd.__name__}')
        await state.reset_state()


@logger.catch
async def send_result_with_photo(callback: CallbackQuery, state: FSMContext, cmd: Callable) -> None:
    photo = callback.data
    logger.info(f'Пользователь  c id {callback.from_user.id} выбрал вывод отелей с фото')
    await callback.message.answer(photo)
    await state.update_data(photo=photo)

    try:
        data = await state.get_data()
        await callback.message.answer('Приступаю к поиску 🔎')
        logger.info(f"Бот приступает к выполнению команды /{cmd.__name__}")
        await callback.message.delete_reply_markup()
        id_city = data.get('id_city')
        days_quantity = (data['departure_date'] - data['arrival_date']).days
        quantity_hotels = data.get('quantity_hotels')
        time = data.get('time')
        hotels = await cmd(data, id_city, days_quantity)
        if hotels:
            if len(hotels) < int(quantity_hotels):
                await callback.message.answer(f'По указанным параметрам удалось найти отелей: {len(hotels)}')
            for hotel in hotels:
                hotel_id = hotel[0]
                photo_dict = await get_photo(hotel_id)
                photo_data = photo_dict[0]
                photo_keyboard = get_photo_keyboard(photo_dict)  # Page: 0
                msg = await bot.send_photo(
                    chat_id=callback.message.chat.id,
                    photo=photo_data.get("image_url"),
                    parse_mode="HTML",
                    reply_markup=photo_keyboard)

                Images.images_dict[msg.message_id] = photo_dict
                hotel_name = hotel[1]
                hotel_address = hotel[2]
                distance_to_center = hotel[3]
                rating = hotel[4]
                one_night_price = hotel[5]
                full_price = hotel[6]
                hotel_link = hotel[7]
                await command.add_hotel(command=cmd.__name__, time=time, id=callback.from_user.id, name=hotel_name,
                                        address=hotel_address,
                                        rating=rating, distance=distance_to_center, night_price=one_night_price,
                                        all_period_price=full_price, link=hotel_link)
                await callback.message.answer(f'Название отеля {hotel_name}\n'
                                              f'\nАдрес: {hotel_address}'
                                              f'\nРасстояние до центра города: {distance_to_center}'
                                              f'\nРейтинг отеля: {rating} ⭐️'
                                              f'\nЦена за ночь: {one_night_price} ₽'
                                              f'\nЦена за весь период: {full_price} ₽'
                                              f'\nСсылка на номер: {hotel_link}')

            await state.reset_state()
            await callback.message.answer('Команда выполнена. Для просмотра всего функционала введите /help')
        else:
            await callback.message.answer('К сожалению по вашему запросу ничего не найдено. Попробуйте изменить '
                                          'критерии поиска и попробовать снова. Для этого введите команду '
                                          f'/{cmd.__name__}')
            await state.reset_state()

    except JSONDecodeError:
        await callback.message.answer('Не получилось найти данные по введенному городу, попробуйте снова.\n'
                                      f'Для этого пропишите команду /{cmd.__name__}')
        await state.finish()
    except TypeError:
        await callback.message.answer('В ходе поиска возникла ошибка, попробуйте снова.\n'
                                      f'Для этого пропишите команду /{cmd.__name__}')
        await state.finish()


@logger.catch
async def scroll_photo(query: CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    try:
        photo_dict = Images.images_dict.get(query.message.message_id)
        page = int(callback_data.get("page"))
        photo_data = photo_dict[page]
        keyboard = get_photo_keyboard(photo_dict, page)

        photo = InputMedia(type="photo", media=photo_data.get("image_url"))
        await query.message.edit_media(photo, keyboard)
        await state.reset_state(with_data=False)
    except Exception as ex:
        logger.exception(ex)
