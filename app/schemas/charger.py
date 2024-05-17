from pydantic import BaseModel


class AddChargerRequest(BaseModel):
    name: str
    type: str
    address: str 
    is_active: bool
    max_power: int
    HA_Entity_ID_state: str
    HA_Entity_ID_current_power: str

class UpdateChargerRequest(AddChargerRequest):
    id: int
