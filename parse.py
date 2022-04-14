import asyncio
from typing import Dict
from loader import headers
import aiohttp
from aiogram import types


async def get_city(city: types.Message):
    async with aiohttp.ClientSession() as session:
        url = "https://hotels4.p.rapidapi.com/locations/v2/search"

        querystring = {"query": city, "locale": "ru_RU", "currency": "RUB"}

        async with session.get(url, headers=headers, params=querystring) as response:
            result = await response.json()
            entities = result.get('suggestions')[0].get('entities')
            name_dict_with_destation_id = dict()

            for elem in entities:
                caption = elem.get('caption')
                name_dict_with_destation_id[caption.replace("<span class='highlighted'>", "").replace("</span>", "")] \
                    = elem.get('destinationId')

            return name_dict_with_destation_id


async def lowprice(data: Dict, id_city, days_quantity):
    async with aiohttp.ClientSession() as session:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        check_in = data["arrival_date"]
        check_out = data["departure_date"]
        querystring = {"destinationId": id_city, "pageNumber": "1", "pageSize": data.get('quantity_hotels'),
                       "checkIn": str(check_in),
                       "checkOut": str(check_out), "adults1": "1", "sortOrder": "PRICE",
                       "locale": "ru_RU", "currency": "RUB"}

        async with session.get(url, headers=headers, params=querystring) as response:
            result = await response.json()
            hotel = result.get('data').get('body').get('searchResults').get('results')
            hotels_list = list()

            for i in hotel:
                my_hotel = (i.get('id'), i.get('name'), i.get('address').get('streetAddress'),
                            i.get('landmarks')[0].get('distance'), f'{i.get("starRating")}⭐️',
                            i.get('ratePlan').get('price').get('exactCurrent'),
                            i.get('ratePlan').get('price').get('exactCurrent') * days_quantity,
                            f'https://hotels.com/ho{i.get("id")}')
                hotels_list.append(my_hotel)

            return hotels_list


async def highprice(data: Dict, id_city, days_quantity):
    async with aiohttp.ClientSession() as session:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        check_in = data["arrival_date"]
        check_out = data["departure_date"]

        querystring = {"destinationId": id_city, "pageNumber": "1", "pageSize": data.get('quantity_hotels'),
                       "checkIn": str(check_in),
                       "checkOut": str(check_out), "adults1": "1", "sortOrder": "PRICE_HIGHEST_FIRST",
                       "locale": "ru_RU", "currency": "RUB"}

        async with session.get(url, headers=headers, params=querystring) as response:
            result = await response.json()
            hotel = result.get('data').get('body').get('searchResults').get('results')
            hotels_list = list()

            for i in hotel:
                my_hotel = (i.get('id'), i.get('name'), i.get('address').get('streetAddress'),
                            i.get('landmarks')[0].get('distance'), f'{i.get("starRating")}⭐️',
                            i.get('ratePlan').get('price').get('exactCurrent'),
                            i.get('ratePlan').get('price').get('exactCurrent') * days_quantity,
                            f'https://hotels.com/ho{i.get("id")}')
                hotels_list.append(my_hotel)

            return hotels_list


async def get_photo(hotel_id):
    async with aiohttp.ClientSession() as session:
        url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

        querystring = {'id': hotel_id}
        async with session.get(url, headers=headers, params=querystring) as response:
            result = await response.json()
            room_images = result.get('roomImages')[0].get('images')
            photo_list = list()
            hotel_images = result.get('hotelImages')
            count = 0

            for i_photo in hotel_images:
                if count != 5:
                    photo_url = i_photo.get('baseUrl').replace('{size}', 'z')
                    photo_list.append({'image_url': photo_url})
                    count += 1
                else:
                    break

            for i_photo in room_images:
                photo_url = i_photo.get('baseUrl').replace('{size}', 'z')
                photo_list.append({'image_url': photo_url})

            return photo_list
