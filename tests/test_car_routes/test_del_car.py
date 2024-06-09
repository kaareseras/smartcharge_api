"""
1. Delete the car with the given ID
2. if the car is not in the DB return 404
3. If the user is not authenticated, return 401
/cars/{car_id}
"""

from app.services.user import _generate_tokens


def test_delete_car( client, car, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }


    response = client.delete(f"/cars/{car.id}", headers=headers)

    assert response.status_code == 200

def test_delete_car_not_existing( client, car, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }


    response = client.delete(f"/cars/-1", headers=headers)

    assert response.status_code == 404


def test_fetch_car_not_authtorised( client, car):  

    response = client.delete(f"/cars/{car.id}")

    assert response.status_code == 401