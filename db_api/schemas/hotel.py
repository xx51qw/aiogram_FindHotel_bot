from sqlalchemy import Column, BigInteger, Integer, String, sql

from db_api.db_gino import TimedBaseModel


class Hotel(TimedBaseModel):
    __tablename__ = 'hotels'
    time = Column(String(100))
    command = Column(String(100))
    id = Column(BigInteger)
    name = Column(String(100))
    address = Column(String(100))
    rating = Column(String(100))
    distance = Column(String(100))
    night_price = Column(Integer)
    all_period_price = Column(BigInteger)
    link = Column(String(100))

    query: sql.Select
