"""
1. Get a list of all chargers without the current status and power
2. Only geet the chargers details if the user is authenticated
3. Get a 404 not found if there is no chargers in the DB
/chargers/{charger_id}
"""

from app.services.user import _generate_tokens


def test_fetch_charger(client, charger, charger2, user, test_session):  
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    response = client.get("/chargers/", headers=headers)

    assert response.status_code == 200



def test_fetch_charger_while_not_logged_in(mock_get_state, client, charger):

    response = client.get("/chargers/")

    assert response.status_code == 401


def test_fetch_charger_with_no_chargers_ib_DB(client, user, test_session):
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    response = client.get("/chargers/", headers = headers)

    assert response.status_code == 404