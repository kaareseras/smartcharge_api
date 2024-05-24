import os
from datetime import datetime, timedelta
import logging
from uuid import uuid1
from fastapi.responses import JSONResponse
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, Response, UploadFile
from app.config.security import generate_token, get_token_payload, hash_password, is_password_strong_enough, load_user, str_decode, str_encode, verify_password
from app.models.car import Car
from app.models.user import User, UserToken
from app.responses.car import CarImageGetResponse, CarImagePostResponse, CarResponse, CarListResponse
from app.services.homeassistant import get_state
from app.services.email import send_account_activation_confirmation_email, send_account_verification_email, send_password_reset_email
from app.services.image import FileToLargeError, ImageTypeError, get_image, save_image
from app.utils.email_context import FORGOT_PASSWORD, USER_VERIFY_ACCOUNT
from app.config.settings import get_settings
from homeassistant_api import  EndpointNotFoundError, UnauthorizedError, MalformedDataError, MalformedInputError, ParameterMissingError, RequestError


settings = get_settings()

async def fetch_car_details(data, session, ha_client):
    car = session.query(Car).filter(Car.id == data).first()
    _error = ""
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")

    _current_SoC=-1
    _current_Max_SoC=-1
    _current_Trip=-1
    _current_pluged_in=False    
    
    try:
        _current_SoC=float(get_state(ha_client, car.HA_Entity_ID_SOC))
        _current_Max_SoC=float(get_state(ha_client, car.HA_Entity_ID_SOC_Max))
        _current_Trip=float(get_state(ha_client, car.HA_Entity_ID_Trip))
        _current_pluged_in=get_state(ha_client, car.HA_Entity_ID_Pluged_In)
    except ValueError as e:
        _error = f"Error converting power to float: {e}"
        logging.error(f"Error converting power to float: {e}")
    except UnauthorizedError as e:
        _error = f"Unauthorized to access HomeAssistant API, check token and URL: {e}"
        logging.error(f"Unauthorized to access HomeAssistant API, check token and URL: {e}")
    except MalformedDataError as e:
        _error = f"Malformed data: {e}"
        logging.error(f"Malformed data: {e}")
    except MalformedInputError as e:
        _error = f"Malformed input: {e}"
        logging.error(f"Malformed input: {e}")
    except ParameterMissingError as e:
        _error = f"Parameter missing: {e}"
        logging.error(f"Parameter missing: {e}")
    except RequestError as e:
        _error = f"Request error: {e}"
        logging.error(f"Request error: {e}")
    except EndpointNotFoundError as e:
        _error = f"Endpoint not found: {e}"
        logging.error(f"Endpoint not found: {e}")
    
    my_car = CarResponse(
        id=car.id,
        name=car.name,
        brand=car.brand,
        model=car.model,
        year=car.year,
        battery_capacity=car.battery_capacity,
        created_at=car.created_at,
        updated_at=car.updated_at,
        image_filename=car.image_filename if car.image_filename else None,
        is_active=car.is_active,
        HA_Entity_ID_SOC=_current_SoC,
        HA_Entity_ID_SOC_Max=_current_Max_SoC,
        HA_Entity_ID_Trip=_current_Trip,
        HA_Entity_ID_Pluged_In=_current_pluged_in,
        error=_error


    )    
    return my_car


async def delete_car(data, session):
    car = session.query(Car).filter(Car.id == data).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")
    session.delete(car)
    session.commit()
    return {"message": "Car deleted successfully."}



async def update_car(data, session, ha_client):
    car = session.query(Car).filter(Car.id == data.id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")

    car.name = data.name
    car.registration = data.registration
    car.brand = data.brand
    car.model = data.model
    car.year = data.year
    car.is_active = data.is_active
    car.battery_capacity = data.battery_capacity
    car.created_at = car.created_at
    car.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(car)

    # Get details for new car and status and power from HomeAssistant

    return await fetch_car_details(car.id, session, ha_client)


async def add_car(data, session, ha_client):
    car = Car()
    car.name = data.name
    car.registration = data.registration
    car.brand = data.brand
    car.model = data.model
    car.year = data.year
    car.is_active = data.is_active
    car.battery_capacity = data.battery_capacity
    car.HA_Entity_ID_Trip = data.HA_Entity_ID_Trip
    car.HA_Entity_ID_SOC = data.HA_Entity_ID_SOC
    car.HA_Entity_ID_SOC_Max = data.HA_Entity_ID_SOC_Max
    car.HA_Entity_ID_Pluged_In = data.HA_Entity_ID_Pluged_In
    car.created_at = datetime.utcnow()
    car.updated_at = datetime.utcnow()
    session.add(car)
    session.commit()
    session.refresh(car)

    # Get details for new car and status and power from HomeAssistant

    return await fetch_car_details(car.id, session, ha_client)


async def fetch_cars(session):  
    cars = session.query(Car).all()

    my_cars = []

    if not cars:
        raise HTTPException(status_code=404, detail="No cars found.")

    for car in cars:
        my_cars.append(CarListResponse(
            id=car.id,
            name=car.name,
            registration=car.registration,
            brand=car.brand,
            model=car.model,
            year=car.year,
            battery_capacity=car.battery_capacity,
            image_filename=car.image_filename if car.image_filename else None,
            is_active=car.is_active

        ))
    return my_cars



async def save_car_image(file: UploadFile, id, session) -> CarImagePostResponse:
    
    car = session.query(Car).filter(Car.id == id).first()
    
    
    if not car:
        return JSONResponse(content={"error": "car not found"}, status_code=404)
    
        
    try:
       unique_name_file_name = save_image(file)
    except ImageTypeError as e:
        return JSONResponse(content={"error": "Only images allowed"}, status_code=403)
    except FileToLargeError as e:
        return JSONResponse(content={"error": "File size too large"}, status_code=403)
    
    
    car.image_filename = unique_name_file_name
    carImageResponse = CarImagePostResponse(file_name = unique_name_file_name)
    session.commit()
    session.refresh(car)

    return carImageResponse



async def get_car_image(id, session) -> Response:
    car = session.query(Car).filter(Car.id == id).first()
    

    if not car:
        return JSONResponse(content={"error": "car not found"}, status_code=404)
    
    if car.image_filename:
        image_filename = car.image_filename
    else:
        logging.info("car not found, return default image")
        image_filename = os.path.join("default_images","default_car.jpg")
  
    try:
        image_bytes = get_image(image_filename)
    except FileNotFoundError:
        logging.info("car image not found, return default image")
        image_filename = os.path.join("default_images","default_car.jpg")
        image_bytes = get_image(image_filename)

    
    # return response
    response = Response(image_bytes, media_type="image/png")
    
    
    return response