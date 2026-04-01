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

    A minimal step that tells the user to use the sidebar panel for advanced
    settings.  Selecting "Save" from this dialog won't change any options —
    the real UI lives at /proportional-light in the sidebar.
    """

    def __init__(self, config_entry):
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
            description_placeholders={
                "panel_url": "/proportional-light",
            },
        )
