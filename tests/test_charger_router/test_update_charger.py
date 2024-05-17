"""
1. update existing charger with new data
2. if charger is ,missing return 404
2. if data is missing return 422
3. If the user is not authenticated, return 401
4. return the updated charger with HA current state and power
/chargers/{charger_id}
"""

from app.services.user import _generate_tokens

def test_update_charger(mock_get_state, client, charger, state_status, state_power, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    } 
    
    updated_charger = {
        "id": charger.id,
        "name": "Javis Charger",
        "type": "Easee",
        "address": "Home",
        "is_active": True,
        "max_power": 100,
        "HA_Entity_ID_state": "sensor.javis_status",
        "HA_Entity_ID_current_power": "sensor.javis_power",
    }

    response = client.put(f"/chargers/{charger.id}", headers=headers, json=updated_charger)

    assert response.status_code == 200
    assert response.json()['id'] is not None   
    assert response.json()['current_state'] == state_status.state
    assert response.json()['current_power'] == float(state_power.state)


def test_update_charger_while_not_logged_in(mock_get_state, client, charger):

    response = client.put(f"/chargers/{charger.id}")

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

    response = client.put(f"/chargers/{charger.id}", headers=headers, json=new_charger)

    assert response.status_code == 422

