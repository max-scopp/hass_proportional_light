"""Proportional Light entity implementation."""
from __future__ import annotations
import asyncio
import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_HS_COLOR,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON

from .const import LOGGER_NAME
from .coordinator import ProportionalLightCoordinator
from .utils import filter_valid_states, get_on_states, add_color_attributes, calculate_proportional_brightness

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
        
        # Ensure the entity gets registered in the light domain
        # This helps with adaptive_lighting compatibility
        safe_name = entry.title.lower().replace(' ', '_').replace('-', '_')
        suggested_entity_id = f"light.{safe_name}"
        
        # Note: Don't set entity_id directly as it can interfere with HA's entity registry
        # Instead, we'll rely on the platform and entity class to handle domain assignment
        _LOGGER.debug(f"ProportionalLight entity initialized: suggested_entity_id={suggested_entity_id}")
    
    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        # Register for coordinator updates
        self.coordinator.add_update_callback(self._handle_coordinator_update)
        
        # Perform initial update
        self.async_write_ha_state()
        
        # Debug logging to help diagnose adaptive_lighting integration issues
        _LOGGER.info(f"ProportionalLight entity added: entity_id={self.entity_id}")
        _LOGGER.info(f"  unique_id={self.unique_id}")
        _LOGGER.info(f"  name={self.name}")
        _LOGGER.info(f"  supported_color_modes={self.supported_color_modes}")
        _LOGGER.info(f"  supported_features={self.supported_features}")
        
        # Also log all light entities that adaptive_lighting can see
        light_entities = self.hass.states.async_entity_ids("light")
        _LOGGER.info(f"All light domain entities visible to adaptive_lighting: {light_entities}")
        
        # Check if this entity is in the light domain entities list
        if self.entity_id in light_entities:
            _LOGGER.info(f"✅ This entity IS visible in light domain entity list")
            
            # Test the _supported_features function from adaptive_lighting 
            state = self.hass.states.get(self.entity_id)
            if state:
                _LOGGER.info(f"Entity state attributes: {state.attributes}")
                
                # Try to replicate adaptive_lighting's _supported_features logic
                supported_features_attr = state.attributes.get("supported_features", 0)
                supported_color_modes_attr = state.attributes.get("supported_color_modes", set())
                _LOGGER.info(f"supported_features attr: {supported_features_attr}")
                _LOGGER.info(f"supported_color_modes attr: {supported_color_modes_attr}")
            else:
                _LOGGER.error(f"Could not get state for {self.entity_id}")
        else:
            _LOGGER.error(f"❌ This entity is NOT visible in light domain entity list!")
            _LOGGER.error(f"   This is why it won't show up in adaptive_lighting configuration!")
    
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
        return temp
    
    @property
    def supported_color_modes(self) -> set[ColorMode] | None:
        """Flag supported color modes."""
        return self.coordinator.supported_color_modes
    
    @property
    def supported_features(self) -> int:
        """Return the supported features of the light."""
        features = 0
        
        # Check if any of the underlying lights support transitions
        if self.coordinator.entities:
            for entity_id in self.coordinator.entities:
                state = self.hass.states.get(entity_id)
                if state:
                    entity_features = state.attributes.get("supported_features", 0)
                    if isinstance(entity_features, int) and entity_features & LightEntityFeature.TRANSITION:
                        features |= LightEntityFeature.TRANSITION
                        break
        
        # Always return at least some basic features to ensure compatibility
        _LOGGER.debug(f"Entity {self._attr_name} calculated supported_features: {features}")
        return features
    
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes to help with adaptive_lighting compatibility."""
        attrs = {}
        
        # Ensure supported_color_modes and supported_features are explicitly available
        if self.supported_color_modes:
            attrs["supported_color_modes"] = list(self.supported_color_modes)
        if self.supported_features:
            attrs["supported_features"] = self.supported_features
            
        # Add color temperature range if available
        if self.min_color_temp_kelvin:
            attrs["min_color_temp_kelvin"] = self.min_color_temp_kelvin
        if self.max_color_temp_kelvin:
            attrs["max_color_temp_kelvin"] = self.max_color_temp_kelvin
            
        return attrs if attrs else None
    
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
        
        # Store group target colors for Apple Music-style behavior
        if ATTR_HS_COLOR in kwargs:
            self.coordinator.set_group_target_color(kwargs[ATTR_HS_COLOR])
        elif ATTR_RGB_COLOR in kwargs:
            # Convert RGB to HS for consistent target storage
            import colorsys
            r, g, b = kwargs[ATTR_RGB_COLOR]
            h_norm, s_norm, _ = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            h, s = h_norm * 360.0, s_norm * 100.0
            self.coordinator.set_group_target_color((h, s))
        elif ATTR_COLOR_TEMP_KELVIN in kwargs:
            self.coordinator.set_group_target_temp(kwargs[ATTR_COLOR_TEMP_KELVIN])
        
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
    
    async def _apply_to_on_lights(self, on_states, target_brightness: int, **kwargs) -> None:
        """Apply settings to currently ON lights with proportional brightness scaling."""
        # Calculate proportional brightness for each light using stored proportions
        proportional_brightnesses, updated_proportions = calculate_proportional_brightness(
            on_states, target_brightness, self.coordinator.brightness_proportions
        )
        
        # Update coordinator with new proportions (for when we're setting the brightness)
        self.coordinator._brightness_proportions.update(updated_proportions)
        
        _LOGGER.debug(f"Applying proportional brightness: target_avg={target_brightness}")
        for entity_id, brightness in proportional_brightnesses.items():
            _LOGGER.debug(f"  {entity_id}: {brightness}")
        
        service_calls = []
        for state in on_states:
            brightness = proportional_brightnesses.get(state.entity_id, target_brightness)
            service_data = {"entity_id": state.entity_id, ATTR_BRIGHTNESS: brightness}
            add_color_attributes(service_data, state.entity_id, self.coordinator.hue_offsets, **kwargs)
            service_calls.append(
                self.hass.services.async_call("light", "turn_on", service_data, blocking=False)
            )
        
        # Execute all service calls concurrently
        if service_calls:
            await asyncio.gather(*service_calls)