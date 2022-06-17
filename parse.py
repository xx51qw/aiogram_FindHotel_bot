import aiohttp
import requests
from aiogram import types
from aiohttp import ContentTypeError
from loguru import logger
from loader import headers
from typing import Dict, List, Union


async def get_city(city: types.Message) -> Dict:
    async with aiohttp.ClientSession() as session:
        url = "https://hotels4.p.rapidapi.com/locations/v2/search"

        querystring = {"query": city, "locale": "ru_RU", "currency": "RUB"}
        async with session.get(url, headers=headers, params=querystring) as response:
            if response.status == 200:
                result = await response.json()
                entities = result.get('suggestions')[0].get('entities')
                name_dict_with_destation_id = dict()
                for elem in entities:
                    caption = elem.get('caption')
                    name_dict_with_destation_id[
                        caption.replace("<span class='highlighted'>", "").replace("</span>", "")] \
                        = elem.get('destinationId')
                return name_dict_with_destation_id


async def lowprice(data: Dict, id_city, days_quantity) -> List:
    async with aiohttp.ClientSession() as session:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        check_in = data["arrival_date"]
        check_out = data["departure_date"]
        querystring = {"destinationId": id_city, "pageNumber": "1", "pageSize": data.get('quantity_hotels'),
                       "checkIn": str(check_in),
                       "checkOut": str(check_out), "adults1": "1", "sortOrder": "PRICE",
                       "locale": "ru_RU", "currency": "RUB"}
        async with session.get(url, headers=headers, params=querystring) as response:
            if response.status == 200:
                result = await response.json()
                hotel = result.get('data').get('body').get('searchResults').get('results')
                hotels_list = list()

                for info in hotel:
                    my_hotel = (info.get('id'), info.get('name'), info.get('address').get('streetAddress'),
                                info.get('landmarks')[0].get('distance'), f'{info.get("starRating")}⭐️',
                                info.get('ratePlan').get('price').get('exactCurrent'),
                                round(info.get('ratePlan').get('price').get('exactCurrent') * days_quantity, 2),
                                f'https://hotels.com/ho{info.get("id")}')

                    hotels_list.append(my_hotel)

                return hotels_list


async def highprice(data: Dict, id_city, days_quantity) -> List:
    async with aiohttp.ClientSession() as session:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        check_in = data["arrival_date"]
        check_out = data["departure_date"]

        querystring = {"destinationId": id_city, "pageNumber": "1", "pageSize": data.get('quantity_hotels'),
                       "checkIn": str(check_in),
                       "checkOut": str(check_out), "adults1": "1", "sortOrder": "PRICE_HIGHEST_FIRST",
                       "locale": "ru_RU", "currency": "RUB"}

        async with session.get(url, headers=headers, params=querystring) as response:
            if response.status == 200:
                result = await response.json()
                hotel = result.get('data').get('body').get('searchResults').get('results')
                hotels_list = list()

                for info in hotel:
                    my_hotel = (info.get('id'), info.get('name'), info.get('address').get('streetAddress'),
                                info.get('landmarks')[0].get('distance'), f'{info.get("starRating")}⭐️',
                                info.get('ratePlan').get('price').get('exactCurrent'),
                                round(info.get('ratePlan').get('price').get('exactCurrent') * days_quantity, 2),
                                f'https://hotels.com/ho{info.get("id")}')

                    hotels_list.append(my_hotel)

                return hotels_list


async def bestdeal(data: Dict, id_city, days_quantity) -> List:
    async with aiohttp.ClientSession() as session:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        check_in = data["arrival_date"]
        check_out = data["departure_date"]
        start_distance = float(data.get('start_distance'))
        finish_distance = float(data.get('finish_distance'))
        hotels_limit = int(data.get('quantity_hotels'))
        hotels_list = list()

        for page_num in range(1, 11):
            querystring = {"destinationId": id_city, "pageNumber": str(page_num), "pageSize": 25,
                           "checkIn": str(check_in), "checkOut": str(check_out), "adults1": "1",
                           "priceMin": data.get('start_price'),
                           "priceMax": data.get('finish_price'), "sortOrder": "DISTANCE_FROM_LANDMARK",
                           "locale": "ru_RU", "currency": "RUB"}
            try:
                async with session.get(url, headers=headers, params=querystring) as response:
                    if response.status == 200:
                        result = await response.json()
                        hotel = result.get('data').get('body').get('searchResults').get('results')

                        for info in hotel:
                            hotel_distance = info.get('landmarks')[0].get('distance').replace('км', '').replace(',',
                                                                                                                '.')
                            if start_distance <= float(hotel_distance) <= finish_distance:
                                my_hotel = (info.get('id'), info.get('name'), info.get('address').get('streetAddress'),
                                            info.get('landmarks')[0].get('distance'), f'{info.get("starRating")}⭐️',
                                            info.get('ratePlan').get('price').get('exactCurrent'),
                                            round(info.get('ratePlan').get('price').get('exactCurrent')
                                                  * days_quantity, 2),
                                            f'https://hotels.com/ho{info.get("id")}')

                                if len(hotels_list) < hotels_limit:
                                    hotels_list.append(my_hotel)

            except ContentTypeError as ex:
                logger.error(ex)
            if len(hotels_list) == hotels_limit:
                break
        return hotels_list


async def get_photo(hotel_id) -> Union[List, Dict]:
    async with aiohttp.ClientSession() as session:
        url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

        querystring = {'id': hotel_id}

        async with session.get(url, headers=headers, params=querystring) as response:
            photo_list = list()
            try:
                result = await response.json()
                room_images = result.get('roomImages')[0].get('images')
                hotel_images = result.get('hotelImages')
                count = 0

                for i_photo in hotel_images:
                    if count != 5:
                        photo_url = i_photo.get('baseUrl').replace('{size}', 'z')
                        if requests.get(photo_url).status_code == 200:
                            photo_list.append({'image_url': photo_url})
                            count += 1
                    else:
                        break

                for i_photo in room_images:
                    if count != 5:
                        photo_url = i_photo.get('baseUrl').replace('{size}', 'z')
                        if requests.get(photo_url).status_code == 200:
                            photo_list.append({'image_url': photo_url})
                            count += 1
                    else:
                        break

            except AttributeError:
                photo_list.append(
                    {'image_url': 'https://proprikol.ru/wp-content/uploads/2020/11/kartinki-oshibki-27.jpg'})

            finally:
                return photo_list
