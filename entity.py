"""Proportional Light entity implementation."""
from __future__ import annotations
import asyncio
import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON

from .const import LOGGER_NAME
from .coordinator import ProportionalLightCoordinator
from .utils import filter_valid_states, get_on_states, add_color_attributes

_LOGGER = logging.getLogger(LOGGER_NAME)


class ProportionalLight(LightEntity):
    """Representation of a Proportional Light."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, coordinator: ProportionalLightCoordinator) -> None:
        """Initialize the proportional light."""
        self.hass = hass
        self.entry = entry
        self.coordinator = coordinator
        self._attr_name = entry.title
        self._attr_unique_id = entry.entry_id
    
    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        # Register for coordinator updates
        self.coordinator.add_update_callback(self._handle_coordinator_update)
        
        # Perform initial update
        self.async_write_ha_state()
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity is being removed from hass."""
        self.coordinator.remove_update_callback(self._handle_coordinator_update)
    
    def _handle_coordinator_update(self) -> None:
        """Handle updates from the coordinator."""
        _LOGGER.debug(f"Entity {self._attr_name} received coordinator update - brightness: {self.coordinator.brightness}")
        self.async_write_ha_state()
    
    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.coordinator.is_on
    
    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return self.coordinator.brightness
    
    @property
    def hs_color(self) -> tuple[float, float] | None:
        """Return the hue and saturation color value [float, float]."""
        color = self.coordinator.hs_color
        if color != getattr(self, '_last_hs_color', None):
            self._last_hs_color = color
            _LOGGER.debug(f"Entity {self._attr_name} hs_color property returning: {color}")
        return color

    @property
    def color_temp_kelvin(self) -> int | None:
        """Return the CT color value in K."""
        temp = self.coordinator.color_temp_kelvin
        if temp != getattr(self, '_last_color_temp', None):
            self._last_color_temp = temp
            _LOGGER.debug(f"Entity {self._attr_name} color_temp_kelvin property returning: {temp}")
        return temp    @property
    def effect(self) -> str | None:
        """Return the current effect."""
        return self.coordinator.effect
    
    @property
    def effect_list(self) -> list[str] | None:
        """Return the list of supported effects."""
        return self.coordinator.effects if self.coordinator.effects else None
    
    @property
    def supported_color_modes(self) -> set[ColorMode] | None:
        """Flag supported color modes."""
        return self.coordinator.supported_color_modes
    
    @property
    def color_mode(self) -> ColorMode | None:
        """Return the color mode of the light."""
        # Return the current active color mode based on what's set
        if self.coordinator.hs_color:
            return ColorMode.HS
        elif self.coordinator.color_temp_kelvin:
            return ColorMode.COLOR_TEMP
        elif self.coordinator.brightness is not None:
            return ColorMode.BRIGHTNESS
        else:
            # Default fallback - use the first supported mode
            supported = self.coordinator.supported_color_modes
            if supported:
                # Return the "best" supported mode in order of preference
                if ColorMode.HS in supported:
                    return ColorMode.HS
                elif ColorMode.COLOR_TEMP in supported:
                    return ColorMode.COLOR_TEMP
                elif ColorMode.BRIGHTNESS in supported:
                    return ColorMode.BRIGHTNESS
                else:
                    return next(iter(supported))
            return ColorMode.BRIGHTNESS
    
    @property
    def min_color_temp_kelvin(self) -> int | None:
        """Return the coldest color_temp_kelvin that this light supports."""
        return self.coordinator.min_color_temp_kelvin
    
    @property
    def max_color_temp_kelvin(self) -> int | None:
        """Return the warmest color_temp_kelvin that this light supports."""
        return self.coordinator.max_color_temp_kelvin
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the proportional light group."""
        states = filter_valid_states(self.hass, self.coordinator.entities)
        if not states:
            return
        
        # Extract brightness and filter it out of kwargs to avoid conflicts
        target_brightness = kwargs.pop(ATTR_BRIGHTNESS, None)
        
        # Get currently ON lights
        on_states = get_on_states(states)
        
        if not on_states:
            # No lights are on - turn on all lights
            brightness = target_brightness or 255
            await self._apply_to_all_lights(states, brightness, **kwargs)
        else:
            # Some lights are on - apply settings to ON lights only
            brightness = target_brightness or self.coordinator.brightness or 255
            await self._apply_to_on_lights(on_states, brightness, **kwargs)
        
        # Update coordinator state
        await self.coordinator.async_update_state()
    
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off all lights in the group."""
        if self.coordinator.entities:
            await self.hass.services.async_call(
                "light", "turn_off", {"entity_id": self.coordinator.entities}, blocking=True
            )
        
        # Update coordinator state
        await self.coordinator.async_update_state()
    
    async def _apply_to_all_lights(self, states, brightness: int, **kwargs) -> None:
        """Apply settings to all lights with the same brightness."""
        service_calls = []
        for state in states:
            service_data = {"entity_id": state.entity_id, ATTR_BRIGHTNESS: brightness}
            add_color_attributes(service_data, state.entity_id, self.coordinator.hue_offsets, **kwargs)
            service_calls.append(
                self.hass.services.async_call("light", "turn_on", service_data, blocking=False)
            )
        
        # Execute all service calls concurrently
        if service_calls:
            await asyncio.gather(*service_calls)
    
    async def _apply_to_on_lights(self, on_states, brightness: int, **kwargs) -> None:
        """Apply settings to currently ON lights with the same brightness."""
        service_calls = []
        for state in on_states:
            service_data = {"entity_id": state.entity_id, ATTR_BRIGHTNESS: brightness}
            add_color_attributes(service_data, state.entity_id, self.coordinator.hue_offsets, **kwargs)
            service_calls.append(
                self.hass.services.async_call("light", "turn_on", service_data, blocking=False)
            )
        
        # Execute all service calls concurrently
        if service_calls:
            await asyncio.gather(*service_calls)