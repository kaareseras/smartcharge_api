from pydantic import BaseModel


class AddCarRequest(BaseModel):
    name : str
    registration : str
    brand : str
    model : str
    year : int
    battery_capacity : int



class UpdateCarRequest(AddCarRequest):
    id: int
