from datetime import datetime
from json import loads
import sys
import os
from typing import Any, Generator
from unittest.mock import Mock, patch

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
def mock_get_state(state_status, state_power) -> Generator[Any, Any, Any]:
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
        }.get(entity_id, None)
    ) as get_state_mock:
        yield get_state_mock


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
    model.img = "charger1.jpg"
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
    model.img = "charger2.jpg"
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

