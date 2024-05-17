from fastapi import APIRouter, BackgroundTasks, Depends, status, Header
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config.database import get_session
from app.config.homeassistant import get_ha_client
from app.responses.charger import ChargerResponse, ChargerListResponse
from app.responses.user import UserResponse, LoginResponse
from app.schemas.user import RegisterUserRequest, ResetRequest, VerifyUserRequest, EmailRequest
from app.schemas.charger import AddChargerRequest
from app.services import user, charger
from app.config.security import get_current_user, oauth2_scheme


charger_router = APIRouter(
    prefix="/chargers",
    tags=["Charger"],
    responses={404: {"description": "Not found"}},
)

@charger_router.get("", status_code=status.HTTP_200_OK, response_model=list[ChargerListResponse])
async def get_charger_info(
    session: Session = Depends(get_session), 
    user = Depends(get_current_user)
):
    return await charger.fetch_chargers(session)

@charger_router.get("/{pk}", status_code=status.HTTP_200_OK, response_model=ChargerResponse)
async def get_charger_info(
    pk, 
    session: Session = Depends(get_session), 
    ha_client = Depends(get_ha_client),
    user = Depends(get_current_user)
):
    return await charger.fetch_charger_details(pk, session, ha_client)

@charger_router.post("",status_code=status.HTTP_200_OK, response_model=ChargerResponse)
async def add_new_charger(
    data: AddChargerRequest,
    session: Session = Depends(get_session), 
    ha_client = Depends(get_ha_client),
    user = Depends(get_current_user),
      
):
    return await charger.add_charger(data, session, ha_client)




@charger_router.delete("/{pk}", status_code=status.HTTP_200_OK)
async def delete_charger(
    pk, 
    session: Session = Depends(get_session), 
    user = Depends(get_current_user)
):
    return await charger.delete_charger(pk, session)