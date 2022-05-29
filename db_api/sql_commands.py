from typing import Any
from loguru import logger
from asyncpg import UniqueViolationError
from db_api.schemas.hotel import Hotel
from db_api.schemas.user import User


@logger.catch
async def add_user(id: int, name: str) -> None:
    try:
        user = User(id=id, name=name)

        await user.create()

    except UniqueViolationError:
        pass


@logger.catch
async def select_user(id: int) -> Any:
    user = await User.query.where(User.id == id).gino.first()

    return user


@logger.catch
async def add_hotel(command: str, time: str, id: int, name: str, address: str, distance: float, night_price: int,
                    all_period_price: int, link: str, rating: str) -> Any:
    hotel = Hotel(command=command, time=time,id=id, name=name, address=address, rating=rating, distance=distance,
                  night_price=night_price,
                  all_period_price=all_period_price, link=link)

    await hotel.create()


@logger.catch
async def choose_hotels(user_id: int) -> Any:
    hotels = await Hotel.query.where(Hotel.id == user_id).gino.all()
    return hotels
