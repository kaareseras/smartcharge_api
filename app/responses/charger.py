from tkinter import image_types
from typing import Union
from datetime import datetime
from app.responses.base import BaseResponse


class ChargerResponse(BaseResponse):
    id: int
    name: str
    type: str
    address: str 
    image_filename:str
    is_active: bool
    max_power: int
    HA_Entity_ID_state: str
    HA_Entity_ID_current_power: str
    created_at: Union[str, None, datetime] = None
    updated_at: Union[str, None, datetime] = None
    current_state: str
    current_power: float
    error: str = None


class ChargerListResponse(BaseResponse):
    id: int
    name: str
    type: str
    address: str 
    image_filename:str
    is_active: bool

class ChargerImagePostResponse(BaseResponse):
    file_name: str

class ChargerImageGetResponse(BaseResponse):
    content: bytes


