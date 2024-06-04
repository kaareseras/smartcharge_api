from tkinter import image_types
from typing import Union
from datetime import datetime
from app.responses.base import BaseResponse


class CarResponse(BaseResponse):
    id: int
    name: str
    registration: str
    brand: str
    model: str
    year: int
    image_filename: str | None
    is_active: bool
    battery_capacity: int
    HA_Entity_ID_Trip: str
    HA_Entity_ID_SOC: str
    HA_Entity_ID_SOC_Max: str
    HA_Entity_ID_Pluged_In: str
    current_trip: float
    current_soc: float
    current_max_soc: float
    current_is_plugged_in: bool
    created_at: Union[str, None, datetime] = None
    updated_at: Union[str, None, datetime] = None
    error: str | None = None



class CarListResponse(BaseResponse):
    id: int
    name: str
    registration: str
    brand: str
    model: str
    year: int
    image_filename: str | None
    is_active: bool
    battery_capacity: int

class CarImagePostResponse(BaseResponse):
    file_name: str

class CarImageGetResponse(BaseResponse):
    content: bytes


