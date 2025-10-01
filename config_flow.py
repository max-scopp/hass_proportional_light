from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_ENTITIES
from homeassistant.helpers import selector

DOMAIN = "proportional_light"

class ProportionalLightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title="Proportional Light",
                data={"entities": user_input[CONF_ENTITIES], "hue_offsets": {}},
            )

        schema = vol.Schema({
            vol.Required(CONF_ENTITIES): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain="light", multiple=True
                )
            ),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ProportionalLightOptionsFlow(config_entry)

class ProportionalLightOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return await self.async_step_options(user_input)

    async def async_step_options(self, user_input=None):
        errors = {}
        entities = self._config_entry.data.get("entities", [])
        hue_offsets = self._config_entry.data.get("hue_offsets", {})

        if user_input is not None:
            # Extract hue offsets from user input
            new_hue_offsets = {}
            for key, value in user_input.items():
                if key.startswith("hue_offset_"):
                    entity_id = key.replace("hue_offset_", "")
                    new_hue_offsets[entity_id] = float(value)
            
            # Update the config entry data directly
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data={
                    "entities": user_input[CONF_ENTITIES],
                    "hue_offsets": new_hue_offsets,
                }
            )
            return self.async_create_entry(title="", data={})

        # Build hue offset schema dynamically based on selected entities
        hue_offset_schema = {}
        for entity_id in entities:
            hue_offset_schema[vol.Optional(f"hue_offset_{entity_id}", default=hue_offsets.get(entity_id, 0.0))] = vol.Coerce(float)

        schema = vol.Schema({
            vol.Required(CONF_ENTITIES, default=entities): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain="light", multiple=True
                )
            ),
            **hue_offset_schema
        })
        return self.async_show_form(step_id="options", data_schema=schema, errors=errors)
