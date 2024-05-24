# Description: Charger model for database table creation.
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from app.config.database import Base


class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150))
    registration = Column(String(150))
    brand = Column(String(150))
    model = Column(String(150))
    year = Column(Integer)
    image_filename = Column(String(255))
    is_active = Column(Boolean, default=True)
    battery_capacity = Column(Integer)
    HA_Entity_ID_Trip = Column(String(255))
    HA_Entity_ID_SOC = Column(String(255))
    HA_Entity_ID_SOC_Max = Column(String(255))
    HA_Entity_ID_Pluged_In = Column(String(255))
    updated_at = Column(DateTime, nullable=True, default=None, onupdate=datetime.now)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
