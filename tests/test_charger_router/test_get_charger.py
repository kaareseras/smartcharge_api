"""
1. Get Charger details including current status
2. Only geet the charger details if the user is authenticated
3. If requesting a charger not in DB return 404
4. If the Home Assistant API returns an error, return the charger details without the current status and power
5. If the power is not a float, return the charger details with the error message
6. If the user is not authenticated, return 401
7. If the Home Assistant API returns an Error, return the charger details with the error message
/chargers/{charger_id}
"""

from datetime import datetime
from homeassistant_api import State, UnauthorizedError, MalformedDataError, MalformedInputError, ParameterMissingError, RequestError
import pytest
from app.services.user import _generate_tokens


def test_fetch_charger(mock_get_state, client, charger, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    state1: State =  State( 
        entity_id="sensor.javis_status",
        attributes={},
        state="ok", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )
    
    state2: State =  State( 
        entity_id="sensor.javis_power",
        attributes={},
        state="999.0", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )
    
    
    mock_get_state.side_effect = lambda entity_id: {
            "sensor.javis_status": state1,
            "sensor.javis_power": state2,
        }.get(entity_id, state1)

    response = client.get(f"/chargers/{charger.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()['id'] == charger.id
    assert response.json()['current_state'] == state1.state
    assert response.json()['current_power'] == float(state2.state)

def test_fetch_charger_with_non_float_power(mock_get_state, client, charger, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    state1: State =  State( 
        entity_id="sensor.javis_status",
        attributes={},
        state="ok", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )
    
    state2: State =  State( 
        entity_id="sensor.javis_power",
        attributes={},
        state="abc", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )
    
    
    mock_get_state.side_effect = lambda entity_id: {
            "sensor.javis_status": state1,
            "sensor.javis_power": state2,
        }.get(entity_id, state1)

    response = client.get(f"/chargers/{charger.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()['id'] == charger.id
    assert response.json()['current_state'] == state1.state
    assert response.json()['current_power'] == -1
    assert response.json()['error'] == f"Error converting power to float: could not convert string to float: 'abc'"


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
def test_fetch_charger_with_error_from_HA_api(mock_get_state,sideeffect, error, client, charger, user, test_session):
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }
    mock_get_state.side_effect = sideeffect

    response = client.get(f"/chargers/{charger.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()['id'] == charger.id
    assert response.json()['current_state'] == ''
    assert response.json()['current_power'] == -1
    assert error in str(response.json()['error'])

def test_fetch_charger_with_wrong_id(mock_get_state, client, charger, user, test_session):
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }
    response = client.get("/chargers/-1", headers=headers)

    assert response.status_code == 404

def test_fetch_charger_while_not_logged_in(mock_get_state, client, charger):

    response = client.get("/chargers/{charger.id}")

    assert response.status_code == 401
