"""
1. Succesfull add a new charger to the DB
2. if data is missing return 422
3. If the user is not authenticated, return 401
4. Succesfull add a new charger to the DB where homeassistant tags are not ok
/chargers/{charger_id}
"""

from datetime import datetime
from homeassistant_api import EndpointNotFoundError, State
from app.services.user import _generate_tokens

def test_add_charger(mock_get_state, client, charger, state_status, state_power, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    new_charger = {
        "name": "Javis Charger",
        "type": "Easee",
        "address": "Home",
        "is_active": True,
        "max_power": 100,
        "HA_Entity_ID_state": "sensor.javis_status",
        "HA_Entity_ID_current_power": "sensor.javis_power",
    }

    response = client.post("/chargers/", headers=headers, json=new_charger)

    assert response.status_code == 200
    assert response.json()['id'] is not None   
    assert response.json()['current_state'] == state_status.state
    assert response.json()['current_power'] == float(state_power.state)


def test_delete_charger_while_not_logged_in(mock_get_state, client, charger):

    response = client.get("/chargers/{charger.id}")

    assert response.status_code == 401


def test_add_charger_with_missing_data(client, charger, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    new_charger = {
        "name": "Javis Charger",
        "type": "Easee",
        "address": "Home",

        "max_power": 100,
        "HA_Entity_ID_state": "sensor.javis_status",
        "HA_Entity_ID_current_power": "sensor.javis_power",
    }

    response = client.post("/chargers/", headers=headers, json=new_charger)

    assert response.status_code == 422

def test_add_charger_with_wrong_homeassistant_tags(mock_get_state,client, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    mock_get_state.side_effect = EndpointNotFoundError("Cannot make request to the endpoint")

    new_charger = {
        "name": "Javis Charger",
        "type": "Easee",
        "address": "Home",
        "is_active": True,
        "max_power": 100,
        "HA_Entity_ID_state": "not_a_valid_status_tag",
        "HA_Entity_ID_current_power": "not_a_valid_power_tag",
    }

    response = client.post("/chargers/", headers=headers, json=new_charger)

    assert response.status_code == 200
    assert response.json()['id'] is not None  
    assert "Cannot make request to the endpoint" in response.json()['error']   

