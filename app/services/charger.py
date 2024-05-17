from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from app.config.security import generate_token, get_token_payload, hash_password, is_password_strong_enough, load_user, str_decode, str_encode, verify_password
from app.models.charger import Charger
from app.models.user import User, UserToken
from app.responses.charger import ChargerResponse
from app.services.homeassistant import get_state
from app.services.email import send_account_activation_confirmation_email, send_account_verification_email, send_password_reset_email
from app.utils.email_context import FORGOT_PASSWORD, USER_VERIFY_ACCOUNT
from app.config.settings import get_settings
from homeassistant_api import  UnauthorizedError, MalformedDataError, MalformedInputError, ParameterMissingError, RequestError


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

    
    my_charger = ChargerResponse(
        id=charger.id,
        name=charger.name,
        type=charger.type,
        address=charger.address,
        img=charger.img,
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


async def add_charger(data, session, ha_client):
    charger = Charger()
    charger.name = data.name
    charger.type = data.type
    charger.address = data.address
    charger.img = ""
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