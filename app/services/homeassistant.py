# Description: This file contains the HomeAssistant class which is responsible for interacting with the Home Assistant API.

from homeassistant_api import State

def get_state(ha_client, entity_id: str ) -> str:
    state: State = ha_client.get_state(entity_id=entity_id)
    value = state.state
    return value