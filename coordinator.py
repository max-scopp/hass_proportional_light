"""Coordinator for managing Proportional Light state updates."""
from __future__ import annotations
import asyncio
import logging
from typing import Any, Callable

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.const import STATE_ON
from homeassistant.components.light import ATTR_BRIGHTNESS

from .const import LOGGER_NAME, CONF_ENTITIES, CONF_HUE_OFFSETS
from .utils import (
    filter_valid_states,
    get_on_states,
    calculate_group_brightness,
    calculate_average_color_and_effect,
    calculate_supported_features,
    calculate_proportional_brightness,
)

_LOGGER = logging.getLogger(LOGGER_NAME)


class ProportionalLightCoordinator:
    """Coordinates state updates between member entities and the proportional light."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.entry = entry
        self._entities: list[str] = entry.data.get(CONF_ENTITIES, [])
        self._hue_offsets: dict[str, float] = entry.data.get(CONF_HUE_OFFSETS, {})
        self._update_callbacks: list[Callable[[], None]] = []
        self._unsub_update_listener = None
        self._unsub_state_listener = None
        
        # Current calculated state
        self._is_on: bool = False
        self._brightness: int | None = None
        self._hs_color: tuple[float, float] | None = None
        self._color_temp_kelvin: int | None = None
        self._effect: str | None = None
        self._supported_color_modes: set = set()
        self._effects: list[str] = []
        self._min_color_temp_kelvin: int | None = None
        self._max_color_temp_kelvin: int | None = None
        
        # Brightness proportions for stable scaling
        self._brightness_proportions: dict[str, float] = {}
    
    @property
    def entities(self) -> list[str]:
        """Return the list of member entities."""
        return self._entities
    
    @property
    def hue_offsets(self) -> dict[str, float]:
        """Return the hue offsets dictionary."""
        return self._hue_offsets
    
    @property
    def brightness_proportions(self) -> dict[str, float]:
        """Return the brightness proportions dictionary."""
        return self._brightness_proportions
    
    @property
    def is_on(self) -> bool:
        """Return if the group is on."""
        return self._is_on
    
    @property
    def brightness(self) -> int | None:
        """Return the brightness."""
        return self._brightness
    
    @property
    def hs_color(self) -> tuple[float, float] | None:
        """Return the HS color."""
        return self._hs_color
    
    @property
    def color_temp_kelvin(self) -> int | None:
        """Return the color temperature in Kelvin."""
        return self._color_temp_kelvin
    
    @property
    def effect(self) -> str | None:
        """Return the current effect."""
        return self._effect
    
    @property
    def supported_color_modes(self) -> set:
        """Return supported color modes."""
        return self._supported_color_modes
    
    @property
    def effects(self) -> list[str]:
        """Return available effects."""
        return self._effects
    
    @property
    def min_color_temp_kelvin(self) -> int | None:
        """Return minimum color temperature."""
        return self._min_color_temp_kelvin
    
    @property
    def max_color_temp_kelvin(self) -> int | None:
        """Return maximum color temperature."""
        return self._max_color_temp_kelvin
    
    async def async_setup(self) -> None:
        """Setup the coordinator."""
        # Track state changes for all member entities
        if self._entities:
            self._unsub_state_listener = async_track_state_change_event(
                self.hass, self._entities, self._state_listener
            )
        
        # Listen for config entry updates
        self._unsub_update_listener = self.entry.add_update_listener(
            self._config_entry_updated
        )
        
        # Perform initial update
        await self.async_update_state()
    
    async def async_unload(self) -> None:
        """Unload the coordinator."""
        if self._unsub_state_listener:
            self._unsub_state_listener()
        if self._unsub_update_listener:
            self._unsub_update_listener()
    
    def add_update_callback(self, callback: Callable[[], None]) -> None:
        """Add a callback to be called when state updates."""
        self._update_callbacks.append(callback)
    
    def remove_update_callback(self, callback: Callable[[], None]) -> None:
        """Remove a callback."""
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)
    
    @callback
    def _state_listener(self, event) -> None:
        """Handle state changes from member entities."""
        entity_id = event.data.get('entity_id')
        new_state = event.data.get('new_state')
        old_state = event.data.get('old_state')
        _LOGGER.debug(f"State change detected for {entity_id}")
        if new_state and old_state:
            old_brightness = old_state.attributes.get(ATTR_BRIGHTNESS) if old_state else None
            new_brightness = new_state.attributes.get(ATTR_BRIGHTNESS) if new_state else None
            _LOGGER.debug(f"  State: {old_state.state if old_state else 'None'} -> {new_state.state}")
            _LOGGER.debug(f"  Brightness: {old_brightness} -> {new_brightness}")
        # Schedule async update
        self.hass.async_create_task(self._handle_state_change())
    
    async def _handle_state_change(self) -> None:
        """Handle state changes with a small delay for state consistency."""
        _LOGGER.debug("_handle_state_change called - updating coordinator state")
        # Small delay to ensure the state has been updated in HA
        await asyncio.sleep(0.05)
        await self.async_update_state()
        self._notify_callbacks()
        _LOGGER.debug("_handle_state_change completed - callbacks notified")
    
    @callback
    def _config_entry_updated(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Handle config entry updates."""
        old_entities = set(self._entities)
        new_entities = set(entry.data.get(CONF_ENTITIES, []))
        
        self._entities = entry.data.get(CONF_ENTITIES, [])
        self._hue_offsets = entry.data.get(CONF_HUE_OFFSETS, {})
        
        # If entities changed, we need to re-setup state tracking
        if old_entities != new_entities:
            # Schedule a full reload to restart with new entity tracking
            self.hass.async_create_task(
                self.hass.config_entries.async_reload(entry.entry_id)
            )
        else:
            # Just update state if only settings changed
            self.hass.async_create_task(self.async_update_state())
            self._notify_callbacks()
    
    async def async_update_state(self) -> None:
        """Update the calculated state based on member entities."""
        _LOGGER.debug("Updating coordinator state")
        
        states = filter_valid_states(self.hass, self._entities)
        if not states:
            self._reset_state()
            return
        
        # Get currently ON lights
        on_states = get_on_states(states)
        self._is_on = len(on_states) > 0
        
        _LOGGER.debug(f"Found {len(on_states)} lights ON out of {len(states)} total")
        
        # Debug: Log all entity states  
        for state in states:
            brightness = state.attributes.get(ATTR_BRIGHTNESS, "No brightness attr")
            _LOGGER.debug(f"Entity {state.entity_id}: state={state.state}, brightness={brightness}")
        
        if self._is_on:
            # Calculate state from ON lights
            old_brightness = self._brightness
            self._brightness = calculate_group_brightness(on_states, self._brightness_proportions)
            _LOGGER.debug(f"Coordinator brightness updated: {old_brightness} -> {self._brightness}")
            
            # Update brightness proportions based on current state
            # This captures the natural proportions when lights change externally
            if self._brightness and self._brightness > 0:
                current_proportions = {}
                for s in on_states:
                    brightness = s.attributes.get(ATTR_BRIGHTNESS, 255)
                    proportion = brightness / self._brightness
                    current_proportions[s.entity_id] = proportion
                
                # Only update if proportions have meaningfully changed or are uninitialized
                if not self._brightness_proportions or any(
                    abs(current_proportions.get(entity_id, 0) - self._brightness_proportions.get(entity_id, 0)) > 0.05
                    for entity_id in current_proportions
                ):
                    self._brightness_proportions.update(current_proportions)
                    _LOGGER.debug(f"Updated brightness proportions: {self._brightness_proportions}")
            
            old_hs_color = self._hs_color
            old_color_temp = self._color_temp_kelvin
            old_effect = self._effect
            
            self._hs_color, self._color_temp_kelvin, self._effect = (
                calculate_average_color_and_effect(on_states, self._hue_offsets)
            )
            
            _LOGGER.debug(f"Coordinator color updated:")
            _LOGGER.debug(f"  HS color: {old_hs_color} -> {self._hs_color}")
            _LOGGER.debug(f"  Color temp: {old_color_temp} -> {self._color_temp_kelvin}")
            _LOGGER.debug(f"  Effect: {old_effect} -> {self._effect}")
            
            # Also log what the entity will see
            _LOGGER.debug(f"Entity will now have: hs_color={self._hs_color}, color_temp_kelvin={self._color_temp_kelvin}, effect={self._effect}")
        else:
            # All lights are off
            _LOGGER.debug("All lights are off, resetting brightness to None")
            self._brightness = None
            self._hs_color = None
            self._color_temp_kelvin = None
            self._effect = None
        
        # Update supported features from all entities
        (
            self._supported_color_modes,
            self._effects,
            self._min_color_temp_kelvin,
            self._max_color_temp_kelvin,
        ) = calculate_supported_features(states)
    
    def _reset_state(self) -> None:
        """Reset all state when no entities are available."""
        self._is_on = False
        self._brightness = None
        self._hs_color = None
        self._color_temp_kelvin = None
        self._effect = None
        self._supported_color_modes = set()
        self._effects = []
        self._min_color_temp_kelvin = None
        self._max_color_temp_kelvin = None
    
    def _notify_callbacks(self) -> None:
        """Notify all registered callbacks of state changes."""
        for callback in self._update_callbacks:
            callback()