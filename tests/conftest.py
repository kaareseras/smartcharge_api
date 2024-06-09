from datetime import datetime
from json import loads
import sys
import os
from typing import Any, Generator
from unittest import mock
from unittest.mock import AsyncMock, Mock, mock_open, patch

from homeassistant_api import State

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.config.email import fm
from app.config.database import Base, get_session
from app.models.charger import Charger
from app.models.car import Car
from app.models.user import User
from app.config.security import hash_password
from app.services.user import _generate_tokens

USER_NAME = "Keshari Nandan"
USER_EMAIL = "keshari@describly.com"
USER_PASSWORD = "123#Describly"

engine = create_engine("sqlite:///./fastapi.db")
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def state_status ():
    state: State =  State( 
        entity_id="sensor.javis_status",
        attributes={},
        state="ok", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )
    return state

@pytest.fixture(scope="function")
def state_power ():
    state: State =  State( 
        entity_id="sensor.javis_power",
        attributes={},
        state="999.0", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )
    return state

@pytest.fixture(scope="function")
def state_trip():
    state: State =  State( 
        entity_id="sensor.tesla_odometer",
        attributes={},
        state="9999.9", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )
    return state

@pytest.fixture(scope="function")
def state_soc():
    state: State =  State( 
        entity_id="sensor.tesla_battery_level",
        attributes={},
        state="45", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )
    return state

@pytest.fixture(scope="function")
def state_soc_max():
    state: State =  State( 
        entity_id="sensor.tesla_charge_limit_soc",
        attributes={},
        state="80", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )
    return state

@pytest.fixture(scope="function")
def state_pluged_in():
    state: State =  State( 
        entity_id="sensor.binary_sensor.tesla_plugged_in",
        attributes={},
        state="on", 
        last_changed=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        context={"id": "1234567890"},
    )
    return state

@pytest.fixture(scope="function")
def mock_get_state(
    state_status, 
    state_power,
    state_trip,
    state_soc,
    state_soc_max,
    state_pluged_in,
) -> Generator[Any, Any, Any]:
    """
    Fixture that mocks the homeassistant_api get_state method.

    Returns:
        Generator: A generator that yields the mock get_state method.
    """

    with patch(
        "homeassistant_api.Client.get_state",
        side_effect = lambda entity_id: {
            "sensor.javis_status": state_status,
            "sensor.javis_power": state_power,
            "sensor.tesla_odometer": state_trip,
            "sensor.tesla_battery_level": state_soc,
            "sensor.tesla_charge_limit_soc": state_soc_max,
            "binary_sensor.javis_pluged_in": state_pluged_in,
        }.get(entity_id, None)
    ) as get_state_mock:
        yield get_state_mock

@pytest.fixture
def mocker_open_image(mocker):
    # Read a mocked /image/image-file
    mocked_image = mocker.mock_open()
    builtin_open = "builtins.open"
    mocker.patch(builtin_open, mocked_image)


@pytest.fixture(scope='session')
def small_image(tmp_path_factory):
    img = tmp_path_factory.getbasetemp() / 'charger1.jpg'
    img.write_bytes(b'spam')
    return img

@pytest.fixture(scope='session')
def mock_path():
    patcher = mock.patch('os.path.exists')
    mock_thing = patcher.start()

@pytest.fixture(scope="function") 
def mock_service_write_file() -> Generator:
    with patch(
        "app.services.image.save_image",
        side_effect = Exception("Invalid type")
    ) as get_mock_service_write_file:
        yield get_mock_service_write_file


@pytest.fixture(scope="function")
def test_session() -> Generator:
    session = SessionTesting()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def app_test():
    Base.metadata.create_all(bind=engine)
    yield app
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(app_test, test_session):
    def _test_db():
        try:
            yield test_session
        finally:
            pass

    app_test.dependency_overrides[get_session] = _test_db
    fm.config.SUPPRESS_SEND = 1
    return TestClient(app_test)

@pytest.fixture(scope="function")
def auth_client(app_test, test_session, user):
    def _test_db():
        try:
            yield test_session
        finally:
            pass

    app_test.dependency_overrides[get_session] = _test_db
    fm.config.SUPPRESS_SEND = 1
    data = _generate_tokens(user, test_session)
    client = TestClient(app_test)
    client.headers['Authorization'] = f"Bearer {data['access_token']}"
    return client


@pytest.fixture(scope="function")
def inactive_user(test_session):
    model = User()
    model.name = USER_NAME
    model.email = USER_EMAIL
    model.password = hash_password(USER_PASSWORD)
    model.updated_at = datetime.utcnow()
    model.is_active = False
    test_session.add(model)
    test_session.commit()
    test_session.refresh(model)
    return model

@pytest.fixture(scope="function")
def user(test_session):
    model = User()
    model.name = USER_NAME
    model.email = USER_EMAIL
    model.password = hash_password(USER_PASSWORD)
    model.updated_at = datetime.utcnow()
    model.verified_at = datetime.utcnow()
    model.is_active = True
    test_session.add(model)
    test_session.commit()
    test_session.refresh(model)
    return model

@pytest.fixture(scope="function")
def unverified_user(test_session):
    model = User()
    model.name = USER_NAME
    model.email = USER_EMAIL
    model.password = hash_password(USER_PASSWORD)
    model.updated_at = datetime.utcnow()
    model.is_active = True
    test_session.add(model)
    test_session.commit()
    test_session.refresh(model)
    return model

@pytest.fixture(scope="function")
def charger (test_session):
    model = Charger()
    model.name = "Javis Charger"
    model.type = "Easee"
    model.address = "Home"
    #model.image_filename = "charger1.jpg"
    model.image_filename = "charger.jpg"
    model.is_active = True
    model.max_power = 100
    model.HA_Entity_ID_state= "sensor.javis_status"
    model.HA_Entity_ID_current_power = "sensor.javis_power"
    model.created_at = datetime.utcnow()
    model.updated_at = datetime.utcnow()
    test_session.add(model)
    test_session.commit()
    test_session.refresh(model)
    return model

@pytest.fixture(scope="function")
def charger2 (test_session):
    model = Charger()
    model.name = "Javis Charger 2"
    model.type = "Easee 2"
    model.address = "Home 2"
    model.image_filename = "charger2.jpg"
    model.is_active = True
    model.max_power = 100
    model.HA_Entity_ID_state= "sensor.javis_status"
    model.HA_Entity_ID_current_power = "sensor.javis_power"
    model.created_at = datetime.utcnow()
    model.updated_at = datetime.utcnow()
    test_session.add(model)
    test_session.commit()
    test_session.refresh(model)
    return model


@pytest.fixture(scope="function")
def car (test_session):
    model = Car()
    model.model = "Tesla"
    model.brand = "Model 3"
    model.year = 2021
    model.name = "Javis"
    model.registration = "DD23920"
    model.image_filename = "Tesla_jpg.jpg"
    model.battery_capacity = 75
    model.is_active = True
    model.HA_Entity_ID_Trip = "sensor.tesla_odometer"
    model.HA_Entity_ID_SOC = "sensor.tesla_battery_level"
    model.HA_Entity_ID_SOC_Max = "sensor.tesla_charge_limit_soc"
    model.HA_Entity_ID_Pluged_In = "binary_sensor.javis_pluged_in"
    model.created_at = datetime.utcnow()
    model.updated_at = datetime.utcnow()
    test_session.add(model)
    test_session.commit()
    test_session.refresh(model)
    return model

@pytest.fixture(scope="function")
def car2 (test_session):
    model = Car()
    model.model = "Tesla"
    model.brand = "Model 3"
    model.year = 2022
    model.name = "Javis_2"
    model.registration = "DD23921"
    model.image_filename = "Tesla_jpg.jpg"
    model.battery_capacity = 75
    model.is_active = True
    model.HA_Entity_ID_Trip = "sensor.tesla_odometer"
    model.HA_Entity_ID_SOC = "sensor.tesla_battery_level"
    model.HA_Entity_ID_SOC_Max = "sensor.tesla_charge_limit_soc"
    model.HA_Entity_ID_Pluged_In = "binary_sensor.javis_pluged_in"
    model.created_at = datetime.utcnow()
    model.updated_at = datetime.utcnow()
    test_session.add(model)
    test_session.commit()
    test_session.refresh(model)
    return model