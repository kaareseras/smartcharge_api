"""
1. Delete the charger with the given ID
2. if the charger is not in the DB return 404
3. If the user is not authenticated, return 401
/chargers/{charger_id}
"""

from app.services.user import _generate_tokens


def test_delete_charger( client, charger, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }


    response = client.delete(f"/chargers/{charger.id}", headers=headers)

    assert response.status_code == 200

def test_delete_charger_not_existing( client, charger, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }


    response = client.delete(f"/chargers/-1", headers=headers)

    assert response.status_code == 404


def test_fetch_charger_not_authtorised( client, charger):  

    response = client.delete(f"/chargers/{charger.id}")

    assert response.status_code == 401