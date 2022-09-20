from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

from database_module.db import Base


class Frame(Base):
    __tablename__ = 'frames'

    id = Column(Integer, primary_key=True)
    time = Column(DateTime)

    boxes = relationship('Box', back_populates='frame')


class Box(Base):
    __tablename__ = 'boxes'

    id = Column(Integer, primary_key=True)
    frame_id = Column(Integer, ForeignKey('frames.id'))
    obj_id = Column(Integer)
    class_name = Column(String(20), nullable=False)
    confidence = Column(Float)
    x_min = Column(Float)
    y_min = Column(Float)
    x_max = Column(Float)
    y_max = Column(Float)

    frame = relationship('Frame', back_populates='boxes')
