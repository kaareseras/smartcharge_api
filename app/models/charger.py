# Description: Charger model for database table creation.
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from app.config.database import Base


class Charger(Base):
    __tablename__ = 'chargers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150))
    type = Column(String(150))
    address = Column(String(255))
    img = Column(String(255))
    is_active = Column(Boolean, default=True)
    max_power = Column(Integer)
    HA_Entity_ID_state = Column(String(255))
    HA_Entity_ID_current_power = Column(String(255))
    updated_at = Column(DateTime, nullable=True, default=None, onupdate=datetime.now)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
