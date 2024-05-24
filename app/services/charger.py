import os
from datetime import datetime, timedelta
import logging
from uuid import uuid1
from fastapi.responses import JSONResponse
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, Response, UploadFile
from app.config.security import generate_token, get_token_payload, hash_password, is_password_strong_enough, load_user, str_decode, str_encode, verify_password
from app.models.charger import Charger
from app.models.user import User, UserToken
from app.responses.charger import ChargerImageGetResponse, ChargerImagePostResponse, ChargerResponse, ChargerListResponse
from app.services.homeassistant import get_state
from app.services.email import send_account_activation_confirmation_email, send_account_verification_email, send_password_reset_email
from app.services.image import FileToLargeError, ImageTypeError, get_image, save_image
from app.utils.email_context import FORGOT_PASSWORD, USER_VERIFY_ACCOUNT
from app.config.settings import get_settings
from homeassistant_api import  EndpointNotFoundError, UnauthorizedError, MalformedDataError, MalformedInputError, ParameterMissingError, RequestError


settings = get_settings()

async def fetch_charger_details(data, session, ha_client):
    charger = session.query(Charger).filter(Charger.id == data).first()
    _error = ""
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found.")

    _current_state=""
    _current_power=-1    
    
    try:
        _current_state=get_state(ha_client, charger.HA_Entity_ID_state)
        _current_power=float(get_state(ha_client, charger.HA_Entity_ID_current_power)) 
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
    
    my_charger = ChargerResponse(
        id=charger.id,
        name=charger.name,
        type=charger.type,
        address=charger.address,
        image_filename=charger.image_filename,
        is_active=charger.is_active,
        max_power=charger.max_power,
        HA_Entity_ID_state=charger.HA_Entity_ID_state,
        HA_Entity_ID_current_power=charger.HA_Entity_ID_current_power,
        created_at=charger.created_at,
        updated_at=charger.updated_at,
        current_state=_current_state,
        current_power=_current_power,
        error=_error


    )    
    return my_charger


async def delete_charger(data, session):
    charger = session.query(Charger).filter(Charger.id == data).first()
    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found.")
    session.delete(charger)
    session.commit()
    return {"message": "Charger deleted successfully."}



async def update_charger(data, session, ha_client):
    charger = session.query(Charger).filter(Charger.id == data.id).first()

    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found.")

    charger.name = data.name
    charger.type = data.type
    charger.address = data.address
    charger.img = charger.image_filename
    charger.is_active = data.is_active
    charger.max_power = data.max_power
    charger.HA_Entity_ID_state = data.HA_Entity_ID_state
    charger.HA_Entity_ID_current_power = data.HA_Entity_ID_current_power
    charger.created_at = charger.created_at
    charger.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(charger)

    # Get details for new charger and status and power from HomeAssistant

    return await fetch_charger_details(charger.id, session, ha_client)


async def add_charger(data, session, ha_client):
    charger = Charger()
    charger.name = data.name
    charger.type = data.type
    charger.address = data.address
    charger.image_filename = ""
    charger.is_active = data.is_active
    charger.max_power = data.max_power
    charger.HA_Entity_ID_state = data.HA_Entity_ID_state
    charger.HA_Entity_ID_current_power = data.HA_Entity_ID_current_power
    charger.created_at = datetime.utcnow()
    charger.updated_at = datetime.utcnow()
    session.add(charger)
    session.commit()
    session.refresh(charger)

    # Get details for new charger and status and power from HomeAssistant

    return await fetch_charger_details(charger.id, session, ha_client)


async def fetch_chargers(session):  
    chargers = session.query(Charger).all()

    my_chargers = []

    if not chargers:
        raise HTTPException(status_code=404, detail="No chargers found.")

    for charger in chargers:
        my_chargers.append(ChargerListResponse(
            id=charger.id,
            name=charger.name,
            type=charger.type,
            address=charger.address,
            image_filename=charger.image_filename if charger.image_filename else None,
            is_active=charger.is_active
        ))
    return my_chargers



async def save_charger_image(file: UploadFile, id, session) -> ChargerImagePostResponse:
    
    charger = session.query(Charger).filter(Charger.id == id).first()
    
    
    if not charger:
        return JSONResponse(content={"error": "Charger not found"}, status_code=404)
    
        
    try:
       unique_name_file_name = save_image(file)
    except ImageTypeError as e:
        return JSONResponse(content={"error": "Only images allowed"}, status_code=403)
    except FileToLargeError as e:
        return JSONResponse(content={"error": "File size too large"}, status_code=403)
    
    
    charger.image_filename = unique_name_file_name
    chargerImageResponse = ChargerImagePostResponse(file_name = unique_name_file_name)
    session.commit()
    session.refresh(charger)

    return chargerImageResponse



async def get_charger_image(id, session) -> Response:
    charger = session.query(Charger).filter(Charger.id == id).first()
    

    if not charger:
        return JSONResponse(content={"error": "Charger not found"}, status_code=404)
    
    if charger.image_filename:
        image_filename = charger.image_filename
    else:
        logging.info("Charger not found, return default image")
        image_filename = os.path.join("default_images","default_charger.jpg")
  
    try:
        image_bytes = get_image(image_filename)
    except FileNotFoundError:
        logging.info("Charger image not found, return default image")
        image_filename = os.path.join("default_images","default_charger.jpg")
        image_bytes = get_image(image_filename)

    
    # return response
    response = Response(image_bytes, media_type="image/png")
    
    
    return response