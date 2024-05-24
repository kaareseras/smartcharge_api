import logging
from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config.database import get_session
from app.config.homeassistant import get_ha_client
from app.models.car import Car
from app.responses.car import CarResponse, CarListResponse, CarImagePostResponse, CarImageGetResponse, CarImagePostResponse
from app.services import car

from app.config.security import get_current_user
from app.schemas.car import AddCarRequest, UpdateCarRequest


car_router = APIRouter(
    prefix="/cars",
    tags=["Car"],
    responses={404: {"description": "Not found"}},
)

@car_router.get("", status_code=status.HTTP_200_OK, response_model=list[CarListResponse])
async def get_car(
    session: Session = Depends(get_session), 
    user = Depends(get_current_user)
):
    return await car.fetch_cars(session)

@car_router.get("/{pk}", status_code=status.HTTP_200_OK, response_model=CarResponse)
async def get_car_info(
    pk, 
    session: Session = Depends(get_session), 
    ha_client = Depends(get_ha_client),
    user = Depends(get_current_user)
):
    return await car.fetch_car_details(pk, session, ha_client)

@car_router.post("",status_code=status.HTTP_200_OK, response_model=CarResponse)
async def add_new_car(
    data: AddCarRequest,
    session: Session = Depends(get_session), 
    ha_client = Depends(get_ha_client),
    user = Depends(get_current_user),
      
):
    return await car.add_car(data, session, ha_client)

@car_router.put("/{pk}",status_code=status.HTTP_200_OK, response_model=CarResponse)
async def update_car(
    data: UpdateCarRequest,
    session: Session = Depends(get_session), 
    ha_client = Depends(get_ha_client),
    user = Depends(get_current_user),
      
):
    return await car.update_car(data, session, ha_client)


@car_router.delete("/{pk}", status_code=status.HTTP_200_OK)
async def delete_charger(
    pk, 
    session: Session = Depends(get_session), 
    user = Depends(get_current_user)
):
    return await car.delete_car(pk, session)

@car_router.post("/image/{id}", status_code=status.HTTP_200_OK, response_model=CarImagePostResponse)
async def create_upload_file(     
    id: int,
    file: UploadFile = File(...), 
    session: Session = Depends(get_session),
    user = Depends(get_current_user),
): 
    return await car.save_car_image(file, id, session)

@car_router.get("/image/{id}", status_code=status.HTTP_200_OK)
async def get_car_image(     
    id: int,
    session: Session = Depends(get_session),
    user = Depends(get_current_user),
): 
    return await car.get_car_image(id, session)