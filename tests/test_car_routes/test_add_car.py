"""
1. Succesfull add a new car to the DB
2. if data is missing return 422
3. If the user is not authenticated, return 401
4. Succesfull add a new car to the DB where homeassistant tags are not ok
/cars/{car_id}
"""

from datetime import datetime
from homeassistant_api import EndpointNotFoundError, State
from app.services.user import _generate_tokens

def test_add_car(mock_get_state, client, state_trip, state_soc, state_soc_max, state_pluged_in, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    new_car = {
        "name": "Javis",
        "registration": "DD23920",
        "brand": "Tesla",
        "model": "Model 3",
        "year": 2021,
        "battery_capacity": 75,
        "HA_Entity_ID_Trip": "sensor.tesla_odometer",
        "HA_Entity_ID_SOC": "sensor.tesla_battery_level",
        "HA_Entity_ID_SOC_Max": "sensor.tesla_charge_limit_soc",
        "HA_Entity_ID_Pluged_In": "binary_sensor.javis_pluged_in",
        "is_active": True
    }

    response = client.post("/cars/", headers=headers, json=new_car)

    assert response.status_code == 200
    assert response.json()['id'] is not None   
    assert response.json()['current_trip'] == float(state_trip.state)
    assert response.json()['current_soc'] == float(state_soc.state)
    assert response.json()['current_max_soc'] == float(state_soc_max.state)
    assert response.json()['current_is_plugged_in'] == bool(state_pluged_in.state)

def test_add_car_with_missing_data(client, charger, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    new_car = {
        "name": "Javis",
        "registration": "DD23920",
        "brand": "Tesla",
        "model": "Model 3",

        "battery_capacity": 75,
        "HA_Entity_ID_Trip": "sensor.tesla_odometer",
        "HA_Entity_ID_SOC": "sensor.tesla_battery_level",
        "HA_Entity_ID_SOC_Max": "sensor.tesla_charge_limit_soc",
        "HA_Entity_ID_Pluged_In": "binary_sensor.javis_pluged_in",
        "is_active": True
    }

    response = client.post("/cars/", headers=headers, json=new_car)

    assert response.status_code == 422

def test_add_car_with_wrong_homeassistant_tags(mock_get_state,client, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    mock_get_state.side_effect = EndpointNotFoundError("Cannot make request to the endpoint")


    new_car = {
        "name": "Javis",
        "registration": "DD23920",
        "brand": "Tesla",
        "model": "Model 3",
        "year": 2021,
        "battery_capacity": 75,
        "HA_Entity_ID_Trip": "not_a_valid_status_tag",
        "HA_Entity_ID_SOC": "not_a_valid_status_tag",
        "HA_Entity_ID_SOC_Max": "not_a_valid_status_tag",
        "HA_Entity_ID_Pluged_In": "not_a_valid_status_tag",
        "is_active": True
    }

    response = client.post("/cars/", headers=headers, json=new_car)

    assert response.status_code == 200
    assert response.json()['id'] is not None   
    assert "Cannot make request to the endpoint" in response.json()['error']

def test_add_car_while_not_logged_in(client, charger):

    response = client.get("/cars/{charger.id}")

    assert response.status_code == 401
