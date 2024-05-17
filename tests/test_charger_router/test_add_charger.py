"""
1. Add a new charger to the DB
2. if data is missing return 422
3. If the user is not authenticated, return 401
/chargers/{charger_id}
"""

from datetime import datetime
from homeassistant_api import State
from app.services.user import _generate_tokens

def test_add_charger(mock_get_state, client, charger, user, test_session):  
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
    assert response.json()['current_state'] == state1.state
    assert response.json()['current_power'] == float(state2.state)


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

