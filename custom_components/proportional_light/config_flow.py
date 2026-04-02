"""
Config flow for Proportional Light.

Minimal entry point: just name. All other configuration (selector, entity props,
proportion reset, etc.) is handled by the frontend panel.
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
)

# Proportion-reset constants (used by coordinator)
CONF_PROPORTION_RESET = "proportion_reset_mode"
CONF_RESET_TIMEOUT = "proportion_reset_timeout"
CONF_DEFAULT_PROPORTIONS = "default_proportions"

PROPORTION_RESET_NEVER = "never"
PROPORTION_RESET_ON_OFF = "on_off"
PROPORTION_RESET_ON_SPECIFIC_BRIGHTNESS = "on_specific_brightness"
PROPORTION_RESET_ON_OFF_AND_SPECIFIC = "on_off_and_specific"


class ProportionalLightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Minimal setup: name only. Configure in panel."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Single step: collect group name, create entry."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input.get("name", "").strip()
            if not name:
                errors["name"] = "name_required"
            else:
                return self.async_create_entry(
                    title=name,
                    data={
                        "name": name,
                        CONF_SELECTOR_TYPE: SELECTOR_TYPE_ENTITIES,
                        CONF_SELECTOR_VALUE: [],
                        CONF_ENTITY_PROPS: {},
                        CONF_PROPORTION_RESET: PROPORTION_RESET_ON_SPECIFIC_BRIGHTNESS,
                        CONF_RESET_TIMEOUT: 28800,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required("name"): selector.TextSelector(),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "note": "After creating the group, open the Proportional Light panel in the sidebar to configure which lights to include and set options."
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ProportionalLightOptionsFlow(config_entry)

class ProportionalLightOptionsFlow(config_entries.OptionsFlow):
    """Options are managed in the panel."""

    def __init__(self, config_entry):
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        """Redirect to the Proportional Light panel in the sidebar."""
        return self.async_abort(
            reason="options_managed_in_panel",
            description_placeholders={
                "panel_url": "/proportional-light",
                "group": self._config_entry.title,
            },
        )
