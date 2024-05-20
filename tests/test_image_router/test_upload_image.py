"""
1. User can upload an image to a valid charger and 
2. User cannot upload image to an invalid charger
3. User cannot upload an image with an invalid type
4. User cannot upload an image that is > 1MB
5. User cannot upload an image of a image type that is not allowed
5. User cannot upload an image if not logged in
"""

from app.services.user import _generate_tokens

def test_file_upload(mocker_open_image, client, charger, state_status, state_power, test_session, user):
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }


    with open("tests/test_image_router/test_images/easee_png.png","rb") as image:
        file = image.read()
    
    # Upload the image
    response = client.post(
        "/image",
        data={
            "type": "charger",
            "id": charger.id
        },
        files={
            "file": ("easee_png.png", file),
        },
        headers=headers
    )
    assert response.status_code == 200

    # Check if the image is uploaded by checking if the charger has an image name matching the result of the upload
    response2 = client.get(f"/chargers/{charger.id}", headers=headers)

    assert response2.status_code == 200
    assert response2.json()["image_filename"] == response.json()["file_name"]

def test_file_upload_to_invalid_charger(client, test_session, user, charger):
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }


    with open("tests/test_image_router/test_images/easee_png.png","rb") as image:
        file = image.read()
    
    # Upload the image
    response = client.post(
        "/image",
        data={
            "type": "charger",
            "id": -1
        },
        files={
            "file": ("easee_png.png", file),
        },
        headers=headers
    )
    assert response.status_code == 404
    assert response.json()["error"] == "Charger not found"

def test_file_upload_to_invalid_type(client, test_session, user, charger):
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }


    with open("tests/test_image_router/test_images/easee_png.png","rb") as image:
        file = image.read()
    
    # Upload the image
    response = client.post(
        "/image",
        data={
            "type": "bad type",
            "id": charger.id
        },
        files={
            "file": ("easee_png.png", file),
        },
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()["error"] == "Invalid type"

def test_file_upload_bigger_than_1MB(client, test_session, user, charger):
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }


    with open("tests/test_image_router/test_images/large.png","rb") as image:
        file = image.read()
    
    # Upload the image
    response = client.post(
        "/image",
        data={
            "type": "charger",
            "id": charger.id
        },
        files={
            "file": ("large.png", file),
        },
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()["error"] == "File size too large"

def test_file_upload_is_not_alowed(client, test_session, user, charger):
    data = _generate_tokens(user, test_session)
    headers = {
        "Authorization": f"Bearer {data['access_token']}"
    }


    with open("tests/test_image_router/test_images/pdf.pdf","rb") as image:
        file = image.read()
    
    # Upload the image
    response = client.post(
        "/image",
        data={
            "type": "charger",
            "id": charger.id
        },
        files={
            "file": ("pdf.pdf", file),
        },
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()["error"] == "Only images allowed"

def test_file_upload_while_not_logged_in(client, test_session, charger):

    with open("tests/test_image_router/test_images/easee_png.png","rb") as image:
        file = image.read()
    
    # Upload the image
    response = client.post(
        "/image",
        data={
            "type": "charger",
            "id": -1
        },
        files={
            "file": ("easee_png.png", file),
        }
    )
    assert response.status_code == 404