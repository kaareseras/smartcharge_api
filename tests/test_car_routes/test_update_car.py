"""
1. update existing car with new data
2. if car is ,missing return 404
2. if data is missing return 422
3. If the user is not authenticated, return 401
4. return the updated car with HA current state and power
/cars/{car_id}
"""

from app.services.user import _generate_tokens

def test_update_car(mock_get_state, client, car, state_trip, state_soc, state_soc_max, state_pluged_in, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    } 
    
    updated_car = {
        "id": car.id,
        "name": "Javis_updated",  #<-- updated
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

    response = client.put(f"/cars/{car.id}", headers=headers, json=updated_car)

    assert response.status_code == 200
    assert response.json()['id'] == car.id 
    assert response.json()['name'] == "Javis_updated"  
    assert response.json()['current_trip'] == float(state_trip.state)
    assert response.json()['current_soc'] == float(state_soc.state)
    assert response.json()['current_max_soc'] == float(state_soc_max.state)
    assert response.json()['current_is_plugged_in'] == bool(state_pluged_in.state)


def test_update_car_while_not_logged_in(mock_get_state, client, car):

    response = client.put(f"/cars/{car.id}")

    assert response.status_code == 401


def test_update_car_with_missing_data(client, charger, car, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    updated_car = {
        "ID": car.id,
        "name": "Javis_updated",  #<-- updated
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

    response = client.put(f"/cars/{car.id}", headers=headers, json=updated_car)

    assert response.status_code == 422

