"""Platform for Proportional Light integration."""
from __future__ import annotations
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import LOGGER_NAME, PARALLEL_UPDATES
from .coordinator import ProportionalLightCoordinator  
from .entity import ProportionalLight

_LOGGER = logging.getLogger(LOGGER_NAME)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Proportional Light from a config entry."""
    # Create coordinator
    coordinator = ProportionalLightCoordinator(hass, entry)
    
    # Setup coordinator
    await coordinator.async_setup()
    
    # Store coordinator in hass data for cleanup
    hass.data.setdefault("proportional_light", {})[entry.entry_id] = coordinator
    
    # Create and add the entity
    entity = ProportionalLight(hass, entry, coordinator)
    async_add_entities([entity], True)
    
    # Force an immediate coordinator update after entity is added
    await coordinator.async_update_state()


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Cleanup coordinator
    coordinator = hass.data.get("proportional_light", {}).pop(entry.entry_id, None)
    if coordinator:
        await coordinator.async_unload()
    
    return True


