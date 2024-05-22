import logging
from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config.database import get_session
from app.config.homeassistant import get_ha_client
from app.responses.charger import ChargerImageGetResponse, ChargerImagePostResponse, ChargerResponse, ChargerListResponse
from app.schemas.charger import AddChargerRequest, UpdateChargerRequest
from app.services import charger
from app.config.security import get_current_user


charger_router = APIRouter(
    prefix="/chargers",
    tags=["Charger"],
    responses={404: {"description": "Not found"}},
)

@charger_router.get("", status_code=status.HTTP_200_OK, response_model=list[ChargerListResponse])
async def get_charger(
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

@charger_router.put("/{pk}",status_code=status.HTTP_200_OK, response_model=ChargerResponse)
async def update_charger(
    data: UpdateChargerRequest,
    session: Session = Depends(get_session), 
    ha_client = Depends(get_ha_client),
    user = Depends(get_current_user),
      
):
    return await charger.update_charger(data, session, ha_client)


@charger_router.delete("/{pk}", status_code=status.HTTP_200_OK)
async def delete_charger(
    pk, 
    session: Session = Depends(get_session), 
    user = Depends(get_current_user)
):
    return await charger.delete_charger(pk, session)

@charger_router.post("/image/{id}", status_code=status.HTTP_200_OK, response_model=ChargerImagePostResponse)
async def create_upload_file(     
    id: int,
    file: UploadFile = File(...), 
    session: Session = Depends(get_session),
    user = Depends(get_current_user),
): 
    return await charger.save_charger_image(file, id, session)

@charger_router.get("/image/{id}", status_code=status.HTTP_200_OK)
async def get_charger_image(     
    id: int,
    session: Session = Depends(get_session),
    user = Depends(get_current_user),
): 
    return await charger.get_charger_image(id, session)