"""
1. User can download the picture for a valid charger
2. User cannot download a picture for an invalid charger
3. User has to be loged in to download a picture
4. if not picture is defined in DB, a default picture is returned
5. if the picture is not found in the file system, a default picture is returned
"""

import unittest
from unittest import mock
from unittest.mock import patch
from fastapi.responses import JSONResponse
from app.services.user import _generate_tokens


def test_user_can_download_picture_for_valid_charger(mock_path, mocker_open_image, client, charger, user ,test_session):
    # Test code for user downloading picture for a valid charger

    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    # Download the image
    response = client.get(
        f"/chargers/image/{charger.id}",
        headers=headers
        
    )

    assert response.status_code == 200

def test_user_cannot_download_picture_for_invalid_charger( client, charger, user ,test_session):
    # Test code for user unable to download picture for an invalid charger
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    # Download the image
    response = client.get(
        "/chargers/image/-1",
        headers=headers
        
    )

    assert response.status_code == 404
    assert response.json() == {"error": "Charger not found"} 

def test_user_has_to_be_logged_in_to_download_picture(client):
    # Test code for user needing to be logged in to download picture

    # Download the image
    response = client.get(
        "/chargers/image/-1"
        
    )

    assert response.status_code == 401

def test_default_picture_returned_if_no_picture_defined_in_db( client, charger, user ,test_session):
    # Test code for default picture being returned if no picture is defined in the database
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    charger.image_filename = None

    # Download the image
    response = client.get(
        f"/chargers/image/{charger.id}",
        headers=headers
        
    )

    assert response.status_code == 200
    assert response.headers["content-length"] == '10887'

def test_default_picture_returned_if_picture_not_found_in_file_system(client, charger, user ,test_session):
    # Test code for default picture being returned if the picture is not found in the file system
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }

    # Download the image
    response = client.get(
        f"/chargers/image/{charger.id}",
        headers=headers
        
    )

    assert response.status_code == 200
    assert response.headers["content-length"] == '10887'

