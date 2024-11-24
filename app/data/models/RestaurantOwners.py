from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base

class RestaurantOwners(Base):
    __tablename__ = 'RestaurantOwners'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('UserAccount.id'))
    restaurant_id = Column(Integer, ForeignKey('Restaurant.id'))


    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return result