"""Constants for the Proportional Light integration."""

DOMAIN = "proportional_light"

# Default values
DEFAULT_NAME = "Proportional Light"
PARALLEL_UPDATES = 1

# ---------------------------------------------------------------------------
# Configuration keys — new selector-based model
# ---------------------------------------------------------------------------
# Selector that determines which entities belong to the group
CONF_SELECTOR_TYPE = "selector_type"   # "entities" | "area" | "device"
CONF_SELECTOR_VALUE = "selector_value"  # area_id | device_id | [entity_id, ...]

# Per-entity property overrides, keyed by entity_id
# { entity_id: { "hue_offset": float, "default_proportion": float } }
CONF_ENTITY_PROPS = "entity_props"

# ---------------------------------------------------------------------------
# Legacy keys — kept for backward-compat migration
# ---------------------------------------------------------------------------
CONF_ENTITIES = "entities"       # old flat list
CONF_HUE_OFFSETS = "hue_offsets"  # old per-entity hue override dict

# Selector type values
SELECTOR_TYPE_ENTITIES = "entities"
SELECTOR_TYPE_AREA = "area"
SELECTOR_TYPE_DEVICE = "device"

# Logging
LOGGER_NAME = f"custom_components.{DOMAIN}"
