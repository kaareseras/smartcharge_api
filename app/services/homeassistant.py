# Description: This file contains the HomeAssistant class which is responsible for interacting with the Home Assistant API.

def get_state(ha_client, entity_id: str ):
    entity = ha_client.get_entity(entity_id=entity_id)
    state = entity.get_state().state
    return state