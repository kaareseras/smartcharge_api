from pydantic import BaseModel


class AddCarRequest(BaseModel):
    name : str
    registration : str
    brand : str
    model : str
    year : int
    battery_capacity : int
    HA_Entity_ID_Trip : str
    HA_Entity_ID_SOC : str
    HA_Entity_ID_SOC_Max : str
    HA_Entity_ID_Pluged_In : str
    is_active : bool




class UpdateCarRequest(AddCarRequest):
    id: int
