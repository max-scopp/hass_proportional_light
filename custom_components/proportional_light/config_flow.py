"""
Config flow for Proportional Light.

Intentionally minimal: the initial flow only asks for a name and a light
selector.  All advanced options (per-light hue offsets, proportion reset
behaviour, etc.) are managed via the custom frontend panel registered in
__init__.py.
"""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_SELECTOR_TYPE,
    CONF_SELECTOR_VALUE,
    CONF_ENTITY_PROPS,
    SELECTOR_TYPE_ENTITIES,
    SELECTOR_TYPE_AREA,
    SELECTOR_TYPE_DEVICE,
)

# ---------------------------------------------------------------------------
# Proportion-reset constants (used by coordinator — defined here for
# historical reasons and imported by coordinator.py)
# ---------------------------------------------------------------------------

CONF_PROPORTION_RESET = "proportion_reset_mode"
CONF_RESET_TIMEOUT = "proportion_reset_timeout"
# Legacy key kept for backward-compat reads
CONF_DEFAULT_PROPORTIONS = "default_proportions"

PROPORTION_RESET_NEVER = "never"
PROPORTION_RESET_ON_OFF = "on_off"
PROPORTION_RESET_ON_SPECIFIC_BRIGHTNESS = "on_specific_brightness"
PROPORTION_RESET_ON_OFF_AND_SPECIFIC = "on_off_and_specific"


class ProportionalLightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """
    Initial setup wizard.

    Asks for a group name and how to select the member lights.
    Everything else is configured via the custom frontend panel.
    """

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input.get("name", "").strip()
            if not name:
                errors["name"] = "name_required"
            else:
                selector_type = user_input.get(CONF_SELECTOR_TYPE, SELECTOR_TYPE_ENTITIES)
                selector_value = user_input.get(CONF_SELECTOR_VALUE, [])

                return self.async_create_entry(
                    title=name,
                    data={
                        "name": name,
                        CONF_SELECTOR_TYPE: selector_type,
                        CONF_SELECTOR_VALUE: selector_value,
                        CONF_ENTITY_PROPS: {},
                        CONF_PROPORTION_RESET: PROPORTION_RESET_ON_SPECIFIC_BRIGHTNESS,
                        CONF_RESET_TIMEOUT: 28800,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required("name", default="My Lights"): selector.TextSelector(),
                vol.Required(CONF_SELECTOR_TYPE, default=SELECTOR_TYPE_ENTITIES): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=SELECTOR_TYPE_ENTITIES, label="Specific lights"),
                            selector.SelectOptionDict(value=SELECTOR_TYPE_AREA, label="Area"),
                            selector.SelectOptionDict(value=SELECTOR_TYPE_DEVICE, label="Device"),
                        ]
                    )
                ),
                # The value field is generic; the panel provides the better UX
                # for area/device pickers.  Here we default to an entity selector.
                vol.Optional(CONF_SELECTOR_VALUE): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="light", multiple=True)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "panel_note": "Advanced options (per-light settings, proportion reset) are available in the Proportional Light panel."
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ProportionalLightOptionsFlow(config_entry)

class ProportionalLightOptionsFlow(config_entries.OptionsFlow):
    """
    Options flow.

    For MVP, displays current group info read-only. Full editing will be
    available in the frontend panel once it's integrated.
    """

    def __init__(self, config_entry):
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        """Show current group configuration."""
        data = self._config_entry.data
        name = data.get("name", "Unnamed")
        selector_type = data.get(CONF_SELECTOR_TYPE, "entities")
        
        # Build a human-readable description of what's in this group
        if selector_type == "entities":
            entity_list = data.get(CONF_SELECTOR_VALUE, [])
            if isinstance(entity_list, list):
                count = len(entity_list)
                description = f"Selected {count} light(s)"
            else:
                description = "Selected entities"
        elif selector_type == "area":
            area_id = data.get(CONF_SELECTOR_VALUE, "—")
            description = f"Area: {area_id}"
        elif selector_type == "device":
            device_id = data.get(CONF_SELECTOR_VALUE, "—")
            description = f"Device: {device_id}"
        else:
            description = "Unknown selector type"

        # Build a read-only display schema
        schema = vol.Schema(
            {
                vol.Optional(
                    "group_name",
                    default=name,
                ): selector.TextSelector(
                    selector.TextSelectorConfig(disabled=True)
                ),
                vol.Optional(
                    "group_info",
                    default=f"Type: {selector_type} • {description}",
                ): selector.TextSelector(
                    selector.TextSelectorConfig(disabled=True)
                ),
            }
        )

        if user_input is not None:
            # No-op: just acknowledge and close
            return self.async_abort(reason="options_saved")

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            description_placeholders={
                "info": "Detailed per-light settings (hue offsets, proportions) will be available in the Proportional Light panel in the sidebar. To edit this group, delete and recreate it, or modify the group via YAML (if you prefer). Changes to entity registries (areas/devices) automatically apply."
            },
        )
