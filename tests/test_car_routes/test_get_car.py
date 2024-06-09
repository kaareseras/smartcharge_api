"""
1. Get Car details including current status
2. Only geet the car details if the user is authenticated
3. If requesting a car not in DB return 404
4. If the Home Assistant API returns an error, return the car details without the current status and power
5. If the power is not a float, return the car details with the error message
6. If the user is not authenticated, return 401
7. If the Home Assistant API returns an Error, return the charger details with the error message
/cars/{car_id}
"""

from datetime import datetime
from homeassistant_api import State, UnauthorizedError, MalformedDataError, MalformedInputError, ParameterMissingError, RequestError
import pytest
from app.services.user import _generate_tokens


def test_fetch_car(mock_get_state, client, car, state_trip, state_soc, state_soc_max, state_pluged_in, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    response = client.get(f"/cars/{car.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()['id'] == car.id
    assert response.json()['current_trip'] == float(state_trip.state)
    assert response.json()['current_soc'] == float(state_soc.state)
    assert response.json()['current_max_soc'] == float(state_soc_max.state)
    assert response.json()['current_is_plugged_in'] == bool(state_pluged_in.state)

def test_fetch_car_with_non_float_state(mock_get_state, client, car, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    state1: State =  State( 
        entity_id="sensor.tesla_odometer",
        attributes={},
        state="ok", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )
    
    state2: State =  State( 
        entity_id="sensor.tesla_battery_level",
        attributes={},
        state="ok", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )

    state3: State =  State( 
        entity_id="sensor.tesla_charge_limit_soc",
        attributes={},
        state="ok", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )
    
    state4: State =  State( 
        entity_id="binary_sensor.javis_pluged_in",
        attributes={},
        state="ok", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )
    
    
    mock_get_state.side_effect = lambda entity_id: {
            "sensor.tesla_odometer": state1,
            "sensor.tesla_battery_level": state2,
            "sensor.tesla_charge_limit_soc": state3,
            "binary_sensor.javis_pluged_in": state4
        }.get(entity_id, state1)

    response = client.get(f"/cars/{car.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()['id'] == car.id 
    assert response.json()['current_trip'] == -1
    assert response.json()['current_soc'] == -1
    assert response.json()['current_max_soc'] == -1
    assert response.json()['current_is_plugged_in'] == False

@pytest.mark.parametrize(
    ("sideeffect", "error"),
    [
        (UnauthorizedError, "Unauthorized to access HomeAssistant API, check token and URL: "),
        (MalformedDataError, "Malformed data: "),
        (MalformedInputError, "Malformed input: "),
        (ParameterMissingError, "Parameter missing: "),
        (RequestError, "Request error: "),
    ],
    ids=["UnauthorizedError", "MalformedDataError", "MalformedInputError", "ParameterMissingError", "RequestError"],
)
def test_fetch_car_with_error_from_HA_api(mock_get_state,sideeffect, error, client, car, user, test_session):
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }
    mock_get_state.side_effect = sideeffect

    response = client.get(f"/cars/{car.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()['id'] == car.id
    assert response.json()['current_trip'] == -1
    assert response.json()['current_soc'] == -1
    assert response.json()['current_max_soc'] == -1
    assert response.json()['current_is_plugged_in'] == False
    assert error in str(response.json()['error'])

def test_fetch_car_with_wrong_id(mock_get_state, client, car, user, test_session):
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }
    response = client.get("/cars/-1", headers=headers)

    assert response.status_code == 404

def test_fetch_charger_while_not_logged_in(mock_get_state, client, car):

    response = client.get("/cars/{car.id}")

    assert response.status_code == 401
