from app.config.settings import get_settings
from typing import Generator

from homeassistant_api import Client

settings = get_settings()

def get_ha_client() -> Generator:
    ha_client = Client(settings.HA_URL, settings.HA_TOKEN,cache_session=False)
    try:
        yield ha_client
    finally:
        pass