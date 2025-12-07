# Copilot Instructions for Proportional Light

**Overview**: This is a Home Assistant custom component that provides a virtual "proportional light" entity that controls a group of physical lights while maintaining their brightness relationships (similar to Apple Music's AirPlay multi-room controls).

## Architecture

### Core Data Flow
1. **Coordinator** (`coordinator.py`): Tracks state changes from member lights, calculates group state
2. **ProportionalLight entity** (`entity.py`): Exposes the virtual light to Home Assistant
3. **Config flow** (`config_flow.py`): YAML-free UI for selecting lights and per-light hue offsets
4. **Utils** (`utils.py`): Stateless calculation functions for brightness, color, and feature aggregation

### Key Design Patterns

**Brightness Proportions**: The "magic" algorithm maintains stable brightness relationships:
- When user sets group to 75%, each light scales proportionally (e.g., if Light A was 2x brighter than Light B, it stays that way)
- Proportions are calculated from ON states and stored in `_brightness_proportions` dict
- Special cases: 100% (255) scales everything to max while maintaining proportions; 1% sets all to minimum

**Group Target State**: Coordinator tracks what the USER commanded vs. what individual lights report:
- `set_group_target_color()` / `set_group_target_temp()` store the command (what UI should show)
- External light changes clear targets after 2s delay (via `_delayed_clear_targets()`), forcing display of averaged values
- This prevents the UI from "jumping" when unrelated external changes occur

**Feature Aggregation**: The entity reports only features supported by ALL member lights:
- `calculate_supported_features()` finds intersection of color modes, color temp ranges
- Entity registers in light domain automatically via `light.LightEntity` inheritance
- Supports adaptive_lighting by explicitly setting `supported_color_modes` attribute

## Important Implementation Details

### Hue Offsets
- Per-light hue adjustments (-180° to +180°) configured in options flow
- Only shown for colorable entities (those with RGB/HS/XY modes)
- Applied in `calculate_average_color()` when computing group color
- Stored in config entry data, NOT entity attributes

### Async State Updates
- `async_setup()` registers two listeners: `async_track_state_change_event` (member lights) and config entry updates
- State listener delays update 50ms (`await asyncio.sleep(0.05)`) to ensure HA state consistency
- Config changes to hue_offsets trigger `async_update_state()` only; entity list changes reload integration

### Color Modes
- Support HS, RGB, XY, COLOR_TEMP modes depending on member lights
- Color mode logic in entity: defaults to HS if available, else COLOR_TEMP, else BRIGHTNESS
- Critical: Return non-empty `supported_color_modes` set or adaptive_lighting will filter out the light

## Common Workflows

### Adding a Feature
1. Define new config option in `config_flow.py` (add to schema)
2. Store in config entry data and retrieve in `coordinator.__init__`
3. Apply logic in appropriate util function (e.g., `calculate_*`)
4. Expose via entity property if user-visible

### Debugging State Issues
- Check logs with `custom_components.proportional_light` logger name
- Coordinator logs brightness calculations and proportion updates
- Entity logs when coordinator updates received and state written
- Watch for "Group target colors cleared" messages (indicates when UI will switch from target to averaged)

### Supporting New Color Modes
- Extend `_simple_color_average()` and `_convert_to_kelvin()` in utils.py
- Update `calculate_supported_features()` intersection logic
- Test with lights reporting the new mode in `supported_color_modes`

## Critical Files

| File | Responsibility |
|------|---|
| `coordinator.py` | State calculation & tracking; coordinates member light updates |
| `entity.py` | Home Assistant light entity; bridges coordinator to HA |
| `utils.py` | Pure calculation functions (no side effects) |
| `config_flow.py` | Setup wizard & options flow; validates colorable entities |
| `const.py` | Constants; minimal — most config stored in entry data |
| `translations/` | i18n strings for config flow UI |

## Testing Patterns

- Manual: Add integration from UI with 2+ lights, check group brightness/color in UI and logs
- Config changes: Modify integration options, verify entity reloads and proportions recalculate
- External changes: Turn on/off member lights externally, verify group state updates and targets clear
- Edge cases: All lights off (group off), mixed colorable/brightness-only lights, single light group
