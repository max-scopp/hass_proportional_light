"""Utility functions for Proportional Light integration."""
from __future__ import annotations
from typing import Any
import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    ATTR_RGB_COLOR,
    ATTR_RGBW_COLOR,
    ATTR_RGBWW_COLOR,
    ATTR_XY_COLOR,
    ColorMode,
)
from homeassistant.const import STATE_ON
from homeassistant.core import State
from homeassistant.util.color import color_temperature_to_rgb
import math

from .const import LOGGER_NAME

_LOGGER = logging.getLogger(LOGGER_NAME)

def calculate_average_brightness(on_states: list[State]) -> int | None:
    """Calculate the average brightness of on states."""
    if not on_states:
        return None
        
    brightness_values = [s.attributes.get(ATTR_BRIGHTNESS, 255) for s in on_states]
    _LOGGER.debug(f"Calculating average brightness from {len(on_states)} ON lights:")
    for i, s in enumerate(on_states):
        brightness = s.attributes.get(ATTR_BRIGHTNESS, 255)
        _LOGGER.debug(f"  {s.entity_id}: brightness={brightness}")
    
    avg_brightness = int(sum(brightness_values) / len(brightness_values)) if brightness_values else None
    _LOGGER.debug(f"Average brightness calculated: {avg_brightness}")
    return avg_brightness


def calculate_average_color_and_effect(
    on_states: list[State], hue_offsets: dict[str, float]
) -> tuple[tuple[float, float] | None, int | None, str | None]:
    """Calculate average color and effect from on states."""
    if not on_states:
        return None, None, None

    # Debug: Log all available attributes for each light
    for s in on_states:
        _LOGGER.debug(f"Light {s.entity_id} all attributes: {dict(s.attributes)}")
        _LOGGER.debug(f"Light {s.entity_id} color attributes:")
        for attr_name in [ATTR_HS_COLOR, ATTR_RGB_COLOR, ATTR_COLOR_TEMP_KELVIN, ATTR_XY_COLOR, ATTR_EFFECT]:
            attr_value = s.attributes.get(attr_name)
            if attr_value is not None:
                _LOGGER.debug(f"  {attr_name}: {attr_value}")
            else:
                _LOGGER.debug(f"  {attr_name}: None")

    # Check for active effects first (but ignore "off" effect)
    effects = [s.attributes.get(ATTR_EFFECT) for s in on_states 
               if s.attributes.get(ATTR_EFFECT) and s.attributes.get(ATTR_EFFECT) != 'off']
    if effects:
        _LOGGER.debug(f"Found active effect: {effects[0]}")
        return None, None, effects[0]  # Use first effect found
    
    # Collect all colors from ON lights for averaging
    import colorsys
    collected_colors = []  # List of (h, s) tuples
    
    for s in on_states:
        # Check the actual color mode of the light to prioritize correctly
        current_color_mode = s.attributes.get('color_mode')
        _LOGGER.debug(f"Light {s.entity_id} current color_mode: {current_color_mode}")
        
        # For lights with true color (not just color temperature), prioritize actual colors
        # even if they're currently in color_temp mode
        supported_modes = s.attributes.get('supported_color_modes', [])
        has_color_support = any(mode in supported_modes for mode in ['hs', 'xy', 'rgb'])
        
        # If light supports colors and has actual color values (not just white), collect those
        if has_color_support and s.attributes.get(ATTR_HS_COLOR):
            h, sat = s.attributes.get(ATTR_HS_COLOR)
            # Only use HS color if it has actual saturation (not just white light)
            if sat > 5:  # More than 5% saturation means it's actually colored
                # Apply hue offset compensation if configured
                if s.entity_id in hue_offsets:
                    offset = hue_offsets[s.entity_id]
                    original_h = (h - offset) % 360  # Remove offset to get original
                    _LOGGER.debug(f"Collecting HS color from {s.entity_id}: ({original_h:.1f}, {sat:.1f}) (offset removed: {offset})")
                    collected_colors.append((original_h, sat))
                else:
                    _LOGGER.debug(f"Collecting HS color from {s.entity_id}: ({h:.1f}, {sat:.1f})")
                    collected_colors.append((h, sat))
            else:
                _LOGGER.debug(f"Light {s.entity_id} has HS color but low saturation ({sat:.1f}%) - treating as white")
        
        # Try RGB color if available and no HS color was collected
        elif s.attributes.get(ATTR_RGB_COLOR):
            r, g, b = s.attributes.get(ATTR_RGB_COLOR)
            # Check if it's actually colored (not just white)
            max_rgb = max(r, g, b)
            min_rgb = min(r, g, b)
            if max_rgb > 0 and (max_rgb - min_rgb) > 10:  # Some color variation
                # Convert RGB to HS for consistency
                h_norm, s_norm, _ = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
                h = h_norm * 360.0
                sat = s_norm * 100.0
                _LOGGER.debug(f"Collecting RGB color from {s.entity_id}: RGB({r},{g},{b}) -> HS({h:.1f}, {sat:.1f})")
                collected_colors.append((h, sat))
            else:
                _LOGGER.debug(f"Light {s.entity_id} has RGB color but appears white: RGB({r},{g},{b})")
        
        # Try XY color
        elif s.attributes.get(ATTR_XY_COLOR):
            x, y = s.attributes.get(ATTR_XY_COLOR)
            _LOGGER.debug(f"Found XY color from {s.entity_id}: ({x:.3f}, {y:.3f}) - skipping for now")
            # For now, skip XY colors and continue to next light
            continue
        
        # If no actual color found, try to convert Kelvin temperature to color
        elif s.attributes.get(ATTR_COLOR_TEMP_KELVIN):
            kelvin = s.attributes.get(ATTR_COLOR_TEMP_KELVIN)
            # Convert Kelvin to RGB using Home Assistant utility, then to HS for averaging
            rgb = color_temperature_to_rgb(kelvin)
            h_norm, s_norm, _ = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
            h = h_norm * 360.0
            sat = s_norm * 100.0
            _LOGGER.debug(f"Converting Kelvin from {s.entity_id}: {kelvin}K -> RGB{rgb} -> HS({h:.1f}, {sat:.1f})")
            collected_colors.append((h, sat))
        elif s.attributes.get('color_temp'):
            # Legacy color_temp in mired
            color_temp = s.attributes.get('color_temp')
            kelvin = int(1000000 / color_temp) if color_temp > 0 else 3000
            rgb = color_temperature_to_rgb(kelvin)
            h_norm, s_norm, _ = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
            h = h_norm * 360.0
            sat = s_norm * 100.0
            _LOGGER.debug(f"Converting legacy color_temp from {s.entity_id}: {color_temp} mired ({kelvin}K) -> RGB{rgb} -> HS({h:.1f}, {sat:.1f})")
            collected_colors.append((h, sat))
    
    # If we collected any colors, average them
    if collected_colors:
        _LOGGER.debug(f"Averaging {len(collected_colors)} colors: {collected_colors}")
        
        # Convert HS colors to RGB for proper averaging
        rgb_colors = []
        for h, s in collected_colors:
            # Convert HS to RGB for averaging
            h_norm = h / 360.0
            s_norm = s / 100.0
            r, g, b = colorsys.hsv_to_rgb(h_norm, s_norm, 1.0)  # Full brightness
            rgb_colors.append((r * 255, g * 255, b * 255))
        
        # Average the RGB values
        avg_r = sum(color[0] for color in rgb_colors) / len(rgb_colors)
        avg_g = sum(color[1] for color in rgb_colors) / len(rgb_colors)
        avg_b = sum(color[2] for color in rgb_colors) / len(rgb_colors)
        
        # Convert back to HS
        h_norm, s_norm, _ = colorsys.rgb_to_hsv(avg_r/255.0, avg_g/255.0, avg_b/255.0)
        avg_h = h_norm * 360.0
        avg_s = s_norm * 100.0
        
        _LOGGER.debug(f"Averaged RGB({avg_r:.0f},{avg_g:.0f},{avg_b:.0f}) -> HS({avg_h:.1f}, {avg_s:.1f})")
        return (avg_h, avg_s), None, None
    
    # Second pass: use color temperature if no actual colors found
    for s in on_states:
        if s.attributes.get(ATTR_COLOR_TEMP_KELVIN):
            kelvin = s.attributes.get(ATTR_COLOR_TEMP_KELVIN)
            _LOGGER.debug(f"Using color temperature from {s.entity_id}: {kelvin}K")
            return None, kelvin, None
        elif s.attributes.get('color_temp'):
            # Some lights might use 'color_temp' instead of 'color_temp_kelvin'
            color_temp = s.attributes.get('color_temp')
            _LOGGER.debug(f"Found legacy color_temp from {s.entity_id}: {color_temp} (conversion needed)")
            # Convert mired to kelvin if needed
            if color_temp:
                kelvin = int(1000000 / color_temp) if color_temp > 0 else 3000
                _LOGGER.debug(f"Converted to kelvin: {kelvin}K")
                return None, kelvin, None
    
    # If no colors found, try averaging color temperatures
    kelvin_values = [s.attributes.get(ATTR_COLOR_TEMP_KELVIN) for s in on_states 
                    if s.attributes.get(ATTR_COLOR_TEMP_KELVIN)]
    if kelvin_values:
        avg_kelvin = int(sum(kelvin_values) / len(kelvin_values))
        _LOGGER.debug(f"Averaged {len(kelvin_values)} kelvin values: {avg_kelvin}K")
        return None, avg_kelvin, None
    
    # Final fallback - if no color information at all, provide a default warm white color
    _LOGGER.debug("No color information found, using default warm white (3000K)")
    return None, 3000, None


def calculate_supported_features(states: list[State]) -> tuple[set[ColorMode], list[str], int | None, int | None]:
    """Calculate supported color modes, effects, and temperature ranges from all entities."""
    modes = set()
    effects = set()
    min_kelvin_values = []
    max_kelvin_values = []
    
    for s in states:
        # Collect supported color modes
        if s.attributes.get("supported_color_modes"):
            modes.update(s.attributes["supported_color_modes"])
        
        # Collect effects
        if s.attributes.get("effect_list"):
            effects.update(s.attributes["effect_list"])
        
        # Collect color temperature ranges
        if s.attributes.get("min_color_temp_kelvin"):
            min_kelvin_values.append(s.attributes["min_color_temp_kelvin"])
        if s.attributes.get("max_color_temp_kelvin"):
            max_kelvin_values.append(s.attributes["max_color_temp_kelvin"])
    
    # Clean up color modes
    if modes and ColorMode.ONOFF in modes and len(modes) > 1:
        modes.remove(ColorMode.ONOFF)
    if not modes:
        modes = {ColorMode.BRIGHTNESS}
    
    # Set temperature ranges (use the intersection of all ranges)
    min_kelvin = max(min_kelvin_values) if min_kelvin_values else None
    max_kelvin = min(max_kelvin_values) if max_kelvin_values else None
    
    return modes, sorted(effects) if effects else [], min_kelvin, max_kelvin


def add_color_attributes(
    service_data: dict, entity_id: str, hue_offsets: dict[str, float], **kwargs
) -> None:
    """Add color/effect attributes to service data with hue offset support."""
    # Priority: effect > hs_color > color_temp > other colors
    if ATTR_EFFECT in kwargs:
        service_data[ATTR_EFFECT] = kwargs[ATTR_EFFECT]
    elif ATTR_HS_COLOR in kwargs:
        if entity_id in hue_offsets:
            # Apply hue offset for this specific entity
            h, s = kwargs[ATTR_HS_COLOR]
            offset_h = (h + hue_offsets[entity_id]) % 360
            service_data[ATTR_HS_COLOR] = (offset_h, s)
        else:
            service_data[ATTR_HS_COLOR] = kwargs[ATTR_HS_COLOR]
    elif ATTR_COLOR_TEMP_KELVIN in kwargs:
        service_data[ATTR_COLOR_TEMP_KELVIN] = kwargs[ATTR_COLOR_TEMP_KELVIN]
    elif ATTR_RGB_COLOR in kwargs:
        service_data[ATTR_RGB_COLOR] = kwargs[ATTR_RGB_COLOR]
    elif ATTR_RGBW_COLOR in kwargs:
        service_data[ATTR_RGBW_COLOR] = kwargs[ATTR_RGBW_COLOR]
    elif ATTR_RGBWW_COLOR in kwargs:
        service_data[ATTR_RGBWW_COLOR] = kwargs[ATTR_RGBWW_COLOR]
    elif ATTR_XY_COLOR in kwargs:
        service_data[ATTR_XY_COLOR] = kwargs[ATTR_XY_COLOR]


def filter_valid_states(hass, entity_ids: list[str]) -> list[State]:
    """Get valid states for the given entity IDs."""
    states = [hass.states.get(e) for e in entity_ids]
    return [s for s in states if s]


def get_on_states(states: list[State]) -> list[State]:
    """Filter states to only include those that are on."""
    return [s for s in states if s.state == STATE_ON]

