# Proportional Light - Modular Architecture

This Home Assistant custom component has been refactored into a clean, modular architecture for better maintainability and code organization.

## File Structure

```
proportional_light/
├── __init__.py          # Integration initialization
├── manifest.json        # Integration manifest
├── const.py            # Constants and configuration keys
├── utils.py            # Utility functions for calculations
├── coordinator.py      # State coordination and updates  
├── entity.py           # Main ProportionalLight entity class
├── light.py            # Platform entry point and setup
├── config_flow.py      # Configuration flow (existing)
└── translations/       # Translation files (existing)
```

## Architecture Overview

### 🎯 **const.py** - Constants and Configuration
- Domain name and integration constants
- Configuration keys and default values
- Logging configuration

### 🔧 **utils.py** - Pure Utility Functions
- `calculate_average_brightness()` - Calculate average brightness from ON lights
- `calculate_average_color_and_effect()` - Calculate average colors/effects with hue offset compensation
- `calculate_supported_features()` - Determine supported capabilities from member entities
- `add_color_attributes()` - Apply color attributes with hue offset support
- `filter_valid_states()` - Get valid entity states
- `get_on_states()` - Filter only ON entities

### 🎮 **coordinator.py** - State Management
- `ProportionalLightCoordinator` class
- Manages state updates from member entities
- Handles configuration changes
- Provides calculated state properties
- Manages entity state tracking and callbacks

### 🏠 **entity.py** - Entity Implementation  
- `ProportionalLight` class extending `LightEntity`
- All Home Assistant entity properties and methods
- Uses coordinator for state information
- Handles turn_on/turn_off service calls
- Clean separation from state calculation logic

### 🚀 **light.py** - Platform Entry Point
- `async_setup_entry()` - Creates coordinator and entity
- `async_unload_entry()` - Cleanup when removing
- Minimal platform boilerplate

## Key Benefits

### ✅ **Separation of Concerns**
- **Coordinator**: Manages state and updates
- **Entity**: Handles Home Assistant integration
- **Utils**: Pure calculation functions
- **Constants**: Centralized configuration

### ✅ **Testability**
- Pure functions in utils can be easily unit tested
- Coordinator logic is isolated and testable
- Clear interfaces between components

### ✅ **Maintainability**
- Single responsibility for each file
- Easy to locate and modify specific functionality
- Clear dependencies and imports

### ✅ **Reusability**
- Utility functions can be reused across different components
- Coordinator pattern can be extended for other features
- Modular design supports future enhancements

## Component Behavior

The component maintains the same functionality as before:

1. **Shows average brightness** of all currently ON member lights
2. **When brightness is changed**, sets ALL currently ON lights to the **same brightness**
3. **Inherits all capabilities** from member entities (color modes, effects, temperature ranges)
4. **Stays in sync** with member entity changes automatically
5. **Supports hue offsets** for individual entities

## Usage

The integration works exactly the same from a user perspective. The modular architecture is purely internal and provides better code organization without changing the external behavior.