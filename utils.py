"""Utility functions for Proportional Light integration."""
from __future__ import annotations
from typing import Any
import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
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

def calculate_group_brightness(on_states: list[State], stored_proportions: dict[str, float] | None = None) -> int | None:
    """Calculate group brightness as the highest brightness of any light.
    
    Simple and intuitive: if your brightest light is at 50%, the group shows 50%.
    No complex calculations - just show the maximum brightness.
    """
    if not on_states:
        return None
    
    brightness_values = [s.attributes.get(ATTR_BRIGHTNESS, 255) for s in on_states]
    max_brightness = max(brightness_values) if brightness_values else None
    
    _LOGGER.debug(f"Group brightness from {len(on_states)} lights: {brightness_values} -> max: {max_brightness}")
    return max_brightness


def calculate_proportional_brightness(
    on_states: list[State], target_brightness: int, stored_proportions: dict[str, float] | None = None
) -> tuple[dict[str, int], dict[str, float]]:
    """Calculate proportional brightness maintaining stable target-based proportions.
    
    Like Apple Music/AirPlay: maintains relative brightness relationships between lights
    while scaling the group to the target level. Each light keeps its proportion.
    
    Special case: 100% (255) means scale all lights to their maximum while maintaining proportions
    
    Returns:
        tuple: (brightness_dict, updated_proportions_dict)
    """
    if not on_states:
        return {}, {}
    
    entity_ids = [s.entity_id for s in on_states]
    
    # Special case: 100% means scale proportionally to maximum
    if target_brightness >= 255:
        _LOGGER.debug("Target is 100% (255) - scaling proportionally to maximum")
        # If no stored proportions, calculate from current state
        if stored_proportions is None:
            current_brightnesses = {}
            for s in on_states:
                current_brightnesses[s.entity_id] = s.attributes.get(ATTR_BRIGHTNESS, 255)
            
            # Find the highest current brightness to use as scaling reference
            max_current = max(current_brightnesses.values()) if current_brightnesses.values() else 255
            if max_current == 0:
                max_current = 255  # Avoid division by zero
            
            # Scale all lights so the brightest one hits 255
            proportions = {}
            for entity_id, brightness in current_brightnesses.items():
                proportions[entity_id] = brightness / max_current
                
            new_brightnesses = {}
            for entity_id in entity_ids:
                new_brightnesses[entity_id] = int(255 * proportions[entity_id])
                if new_brightnesses[entity_id] < 1:
                    new_brightnesses[entity_id] = 1
        else:
            # Use stored proportions, scale so highest proportion hits 255
            max_proportion = max(stored_proportions.get(eid, 1.0) for eid in entity_ids)
            proportions = {entity_id: stored_proportions.get(entity_id, 1.0) for entity_id in entity_ids}
            new_brightnesses = {}
            for entity_id in entity_ids:
                new_brightnesses[entity_id] = int(255 * (proportions[entity_id] / max_proportion))
                if new_brightnesses[entity_id] < 1:
                    new_brightnesses[entity_id] = 1
                    
        return new_brightnesses, proportions
    
    # Special case: 0% means all lights at minimum  
    if target_brightness <= 1:
        _LOGGER.debug("Target is 0% (1) - setting all lights to minimum brightness")
        new_brightnesses = {entity_id: 1 for entity_id in entity_ids}
        # Keep existing proportions
        if stored_proportions is None:
            proportions = {entity_id: 1.0 for entity_id in entity_ids}
        else:
            proportions = {entity_id: stored_proportions.get(entity_id, 1.0) for entity_id in entity_ids}
        return new_brightnesses, proportions
    
    # Normal case: Proportional scaling
    # If no stored proportions, calculate from current state
    if stored_proportions is None:
        current_brightnesses = {}
        for s in on_states:
            current_brightnesses[s.entity_id] = s.attributes.get(ATTR_BRIGHTNESS, 255)
        
        current_avg = sum(current_brightnesses.values()) / len(current_brightnesses)
        _LOGGER.debug(f"Initializing proportions from current state (avg: {current_avg:.1f})")
        
        if current_avg == 0:
            # All lights at 0 - start with equal proportions
            proportions = {entity_id: 1.0 for entity_id in entity_ids}
            _LOGGER.debug("All lights at 0, using equal proportions (1.0 each)")
        else:
            # Calculate proportions relative to current average
            proportions = {}
            for entity_id, brightness in current_brightnesses.items():
                proportions[entity_id] = brightness / current_avg
                _LOGGER.debug(f"  {entity_id}: {brightness} / {current_avg:.1f} = {proportions[entity_id]:.3f}")
    else:
        # Use stored proportions, but only for entities that are currently on
        proportions = {entity_id: stored_proportions.get(entity_id, 1.0) for entity_id in entity_ids}
        _LOGGER.debug(f"Using stored proportions: {proportions}")
    
    # Calculate target brightness for each light based on stable proportions
    new_brightnesses = {}
    for entity_id in entity_ids:
        # Calculate ideal brightness based on target and proportion
        ideal_brightness = target_brightness * proportions[entity_id]
        # Clamp to valid range
        actual_brightness = max(1, min(255, int(ideal_brightness)))
        new_brightnesses[entity_id] = actual_brightness
        
        _LOGGER.debug(f"  {entity_id}: target={target_brightness} × {proportions[entity_id]:.3f} = {ideal_brightness:.1f} -> {actual_brightness}")
    
    # Verify the result
    actual_avg = sum(new_brightnesses.values()) / len(new_brightnesses)
    _LOGGER.debug(f"Target brightness: {target_brightness}, achieved: {actual_avg:.1f}")
    
    return new_brightnesses, proportions


def _simple_color_average(colors: list[tuple[float, float]]) -> tuple[tuple[float, float], None, None]:
    """Simple color averaging using Home Assistant's approach.
    
    Just average the hue and saturation values - let HA handle the complexity.
    This creates intuitive results like blue + red = purple.
    """
    if len(colors) == 1:
        return colors[0], None, None
    
    # Simple averaging - works well for most cases
    avg_h = sum(h for h, s in colors) / len(colors)
    avg_s = sum(s for h, s in colors) / len(colors)
    
    _LOGGER.debug(f"Simple color average: {colors} -> HS({avg_h:.1f}, {avg_s:.1f})")
    return (avg_h, avg_s), None, None


def calculate_average_color(
    on_states: list[State], hue_offsets: dict[str, float]
) -> tuple[tuple[float, float] | None, int | None]:
    """Calculate average color from on states."""
    if not on_states:
        return None, None

    # Debug: Log all available attributes for each light
    for s in on_states:
        _LOGGER.debug(f"Light {s.entity_id} all attributes: {dict(s.attributes)}")
        _LOGGER.debug(f"Light {s.entity_id} color attributes:")
        for attr_name in [ATTR_HS_COLOR, ATTR_RGB_COLOR, ATTR_COLOR_TEMP_KELVIN, ATTR_XY_COLOR]:
            attr_value = s.attributes.get(attr_name)
            if attr_value is not None:
                _LOGGER.debug(f"  {attr_name}: {attr_value}")
            else:
                _LOGGER.debug(f"  {attr_name}: None")
    
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
                # Use the actual current color (what the light actually looks like)
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
    
    # If we collected any colors, average them intelligently
    if collected_colors:
        _LOGGER.debug(f"Averaging {len(collected_colors)} colors: {collected_colors}")
        
        avg_color, _, _ = _simple_color_average(collected_colors)
        return avg_color, None
    
    # Second pass: use color temperature if no actual colors found
    for s in on_states:
        if s.attributes.get(ATTR_COLOR_TEMP_KELVIN):
            kelvin = s.attributes.get(ATTR_COLOR_TEMP_KELVIN)
            _LOGGER.debug(f"Using color temperature from {s.entity_id}: {kelvin}K")
            return None, kelvin
        elif s.attributes.get('color_temp'):
            # Some lights might use 'color_temp' instead of 'color_temp_kelvin'
            color_temp = s.attributes.get('color_temp')
            _LOGGER.debug(f"Found legacy color_temp from {s.entity_id}: {color_temp} (conversion needed)")
            # Convert mired to kelvin if needed
            if color_temp:
                kelvin = int(1000000 / color_temp) if color_temp > 0 else 3000
                _LOGGER.debug(f"Converted to kelvin: {kelvin}K")
                return None, kelvin
    
    # If no colors found, try averaging color temperatures
    kelvin_values = [s.attributes.get(ATTR_COLOR_TEMP_KELVIN) for s in on_states 
                    if s.attributes.get(ATTR_COLOR_TEMP_KELVIN)]
    if kelvin_values:
        avg_kelvin = int(sum(kelvin_values) / len(kelvin_values))
        _LOGGER.debug(f"Averaged {len(kelvin_values)} kelvin values: {avg_kelvin}K")
        return None, avg_kelvin
    
    # Final fallback - if no color information at all, provide a default warm white color
    _LOGGER.debug("No color information found, using default warm white (3000K)")
    return None, 3000


def calculate_supported_features(states: list[State]) -> tuple[set[ColorMode], int | None, int | None]:
    """Calculate supported color modes and temperature ranges from all entities."""
    import logging
    
    _LOGGER = logging.getLogger(__name__)
    modes = set()
    min_kelvin_values = []
    max_kelvin_values = []
    
    _LOGGER.debug(f"calculate_supported_features called with {len(states)} states")
    
    for s in states:
        # Collect supported color modes
        entity_modes = s.attributes.get("supported_color_modes")
        _LOGGER.debug(f"Entity {s.entity_id} reports supported_color_modes: {entity_modes}")
        
        if entity_modes:
            modes.update(entity_modes)
        else:
            # Fallback: try to infer from state attributes
            _LOGGER.debug(f"No supported_color_modes found, inferring from attributes")
            if s.attributes.get("hs_color") is not None:
                modes.add(ColorMode.HS)
                _LOGGER.debug(f"  Added HS mode (has hs_color)")
            if s.attributes.get("color_temp_kelvin") is not None or s.attributes.get("color_temp") is not None:
                modes.add(ColorMode.COLOR_TEMP)
                _LOGGER.debug(f"  Added COLOR_TEMP mode (has color_temp)")
            if s.attributes.get("brightness") is not None or s.state == "on":
                modes.add(ColorMode.BRIGHTNESS)
                _LOGGER.debug(f"  Added BRIGHTNESS mode (has brightness or is on)")
        
        # Collect color temperature ranges
        if s.attributes.get("min_color_temp_kelvin"):
            min_kelvin_values.append(s.attributes["min_color_temp_kelvin"])
        if s.attributes.get("max_color_temp_kelvin"):
            max_kelvin_values.append(s.attributes["max_color_temp_kelvin"])
    
    # Clean up color modes
    if modes and ColorMode.ONOFF in modes and len(modes) > 1:
        modes.remove(ColorMode.ONOFF)
    if not modes:
        _LOGGER.debug("No color modes found, defaulting to BRIGHTNESS")
        modes = {ColorMode.BRIGHTNESS}
    
    _LOGGER.debug(f"Final calculated modes: {modes}")
    
    # Set temperature ranges (use the intersection of all ranges)
    min_kelvin = max(min_kelvin_values) if min_kelvin_values else None
    max_kelvin = min(max_kelvin_values) if max_kelvin_values else None
    
    return modes, min_kelvin, max_kelvin


def add_color_attributes(
    service_data: dict, entity_id: str, hue_offsets: dict[str, float], **kwargs
) -> None:
    """Add color attributes to service data with hue offset support."""
    import colorsys
    
    _LOGGER.debug(f"add_color_attributes called for {entity_id} with hue_offsets: {hue_offsets}, kwargs: {kwargs}")
    
    # Priority: hs_color > color_temp > other colors
    if ATTR_HS_COLOR in kwargs:
        if entity_id in hue_offsets:
            # Apply hue offset for this specific entity
            h, s = kwargs[ATTR_HS_COLOR]
            offset_h = (h + hue_offsets[entity_id]) % 360
            service_data[ATTR_HS_COLOR] = (offset_h, s)
            _LOGGER.debug(f"Applied hue offset {hue_offsets[entity_id]}° to {entity_id}: {h}° -> {offset_h}°")
        else:
            service_data[ATTR_HS_COLOR] = kwargs[ATTR_HS_COLOR]
    elif ATTR_COLOR_TEMP_KELVIN in kwargs:
        service_data[ATTR_COLOR_TEMP_KELVIN] = kwargs[ATTR_COLOR_TEMP_KELVIN]
    elif ATTR_RGB_COLOR in kwargs:
        if entity_id in hue_offsets:
            # Apply hue offset by converting RGB -> HS -> offset -> RGB
            r, g, b = kwargs[ATTR_RGB_COLOR]
            h_norm, s_norm, v_norm = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            h = h_norm * 360.0
            offset_h = (h + hue_offsets[entity_id]) % 360
            offset_h_norm = offset_h / 360.0
            
            # Convert back to RGB
            r_new, g_new, b_new = colorsys.hsv_to_rgb(offset_h_norm, s_norm, v_norm)
            service_data[ATTR_RGB_COLOR] = (int(r_new * 255), int(g_new * 255), int(b_new * 255))
            _LOGGER.debug(f"Applied hue offset {hue_offsets[entity_id]}° to {entity_id}: RGB({r},{g},{b}) -> RGB({int(r_new * 255)},{int(g_new * 255)},{int(b_new * 255)})")
        else:
            service_data[ATTR_RGB_COLOR] = kwargs[ATTR_RGB_COLOR]
    elif ATTR_RGBW_COLOR in kwargs:
        service_data[ATTR_RGBW_COLOR] = kwargs[ATTR_RGBW_COLOR]
    elif ATTR_RGBWW_COLOR in kwargs:
        service_data[ATTR_RGBWW_COLOR] = kwargs[ATTR_RGBWW_COLOR]
    elif ATTR_XY_COLOR in kwargs:
        if entity_id in hue_offsets:
            # Apply hue offset by converting XY -> HS -> offset -> XY
            from homeassistant.util.color import color_xy_to_hs, color_hs_to_xy
            x, y = kwargs[ATTR_XY_COLOR]
            try:
                # Convert XY to HS
                h, s = color_xy_to_hs(x, y)
                # Apply hue offset
                offset_h = (h + hue_offsets[entity_id]) % 360
                # Convert back to XY
                new_x, new_y = color_hs_to_xy(offset_h, s)
                service_data[ATTR_XY_COLOR] = (new_x, new_y)
                _LOGGER.debug(f"Applied hue offset {hue_offsets[entity_id]}° to {entity_id}: XY({x:.3f},{y:.3f}) -> HS({h:.1f},{s:.1f}) -> HS({offset_h:.1f},{s:.1f}) -> XY({new_x:.3f},{new_y:.3f})")
            except Exception as e:
                _LOGGER.warning(f"Failed to apply hue offset to XY color for {entity_id}: {e}")
                service_data[ATTR_XY_COLOR] = kwargs[ATTR_XY_COLOR]
        else:
            service_data[ATTR_XY_COLOR] = kwargs[ATTR_XY_COLOR]


def filter_valid_states(hass, entity_ids: list[str]) -> list[State]:
    """Get valid states for the given entity IDs."""
    states = [hass.states.get(e) for e in entity_ids]
    return [s for s in states if s]


def get_on_states(states: list[State]) -> list[State]:
    """Filter states to only include those that are on."""
    return [s for s in states if s.state == STATE_ON]

