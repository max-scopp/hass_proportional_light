from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_ENTITIES
from homeassistant.helpers import selector

DOMAIN = "proportional_light"

CONF_PROPORTION_RESET = "proportion_reset_mode"
CONF_RESET_TIMEOUT = "proportion_reset_timeout"

PROPORTION_RESET_NEVER = "never"
PROPORTION_RESET_ON_OFF = "on_off"
PROPORTION_RESET_ON_SPECIFIC_BRIGHTNESS = "on_specific_brightness"
PROPORTION_RESET_ON_OFF_AND_SPECIFIC = "on_off_and_specific"

def _is_colorable_entity(hass, entity_id: str) -> bool:
    """Check if an entity supports color (RGB/HS modes)."""
    state = hass.states.get(entity_id)
    if not state:
        return False
    
    supported_modes = state.attributes.get("supported_color_modes", [])
    # Check if entity supports any color modes that allow RGB/HS colors
    colorable_modes = {"hs", "xy", "rgb", "rgbw", "rgbww"}
    return any(mode in supported_modes for mode in colorable_modes)


class ProportionalLightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title="Proportional Light",
                data={
                    "entities": user_input[CONF_ENTITIES],
                    "hue_offsets": {},
                    CONF_PROPORTION_RESET: PROPORTION_RESET_ON_SPECIFIC_BRIGHTNESS,
                    CONF_RESET_TIMEOUT: 28800,  # 8 hours in seconds
                },
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
        return await self.async_step_lights(user_input)

    async def async_step_lights(self, user_input=None):
        """Step 1: Configure lights"""
        errors = {}
        entities = self._config_entry.data.get("entities", [])

        if user_input is not None:
            # Store selected entities and move to next step
            self._entities = user_input[CONF_ENTITIES]
            return await self.async_step_proportions()

        schema = vol.Schema({
            vol.Required(CONF_ENTITIES, default=entities): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain="light", multiple=True
                )
            ),
        })
        
        return self.async_show_form(
            step_id="lights",
            data_schema=schema,
            errors=errors,
            description_placeholders={"note": "Select the lights to include in this proportional group"}
        )

    async def async_step_proportions(self, user_input=None):
        """Step 2: Configure proportion reset behavior"""
        errors = {}
        proportion_reset = self._config_entry.data.get(CONF_PROPORTION_RESET, PROPORTION_RESET_ON_SPECIFIC_BRIGHTNESS)
        reset_timeout = self._config_entry.data.get(CONF_RESET_TIMEOUT, 28800)

        if user_input is not None:
            self._proportion_reset = user_input[CONF_PROPORTION_RESET]
            self._reset_timeout = user_input[CONF_RESET_TIMEOUT]
            return await self.async_step_colors()

        schema = vol.Schema({
            vol.Required(CONF_PROPORTION_RESET, default=proportion_reset): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value=PROPORTION_RESET_NEVER, label="Never reset"),
                        selector.SelectOptionDict(value=PROPORTION_RESET_ON_OFF, label="Reset on turn off"),
                        selector.SelectOptionDict(value=PROPORTION_RESET_ON_SPECIFIC_BRIGHTNESS, label="Reset when turned on with specific brightness"),
                        selector.SelectOptionDict(value=PROPORTION_RESET_ON_OFF_AND_SPECIFIC, label="Reset on both"),
                    ]
                )
            ),
            vol.Required(CONF_RESET_TIMEOUT, default=reset_timeout): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=86400,
                    step=300,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="s"
                )
            ),
        })
        
        return self.async_show_form(
            step_id="proportions",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "info": "Control when brightness proportions are reset. See README for detailed explanations of each mode."
            }
        )

    async def async_step_colors(self, user_input=None):
        """Step 3: Configure hue offsets for colorable lights"""
        errors = {}
        hue_offsets = self._config_entry.data.get("hue_offsets", {})
        
        # Get colorable entities from the selected lights
        colorable_entities = [entity_id for entity_id in self._entities if _is_colorable_entity(self.hass, entity_id)]

        if user_input is not None:
            # Extract hue offsets from user input
            new_hue_offsets = {}
            for key, value in user_input.items():
                if key.startswith("hue_offset_"):
                    entity_id = key.replace("hue_offset_", "")
                    if _is_colorable_entity(self.hass, entity_id):
                        new_hue_offsets[entity_id] = float(value)
            
            # Update the config entry data
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data={
                    "entities": self._entities,
                    "hue_offsets": new_hue_offsets,
                    CONF_PROPORTION_RESET: self._proportion_reset,
                    CONF_RESET_TIMEOUT: self._reset_timeout,
                }
            )
            return self.async_create_entry(title="", data={})

        # Build hue offset schema
        hue_offset_schema = {}
        for entity_id in colorable_entities:
            state = self.hass.states.get(entity_id)
            friendly_name = state.attributes.get("friendly_name", entity_id) if state else entity_id
            field_name = f"hue_offset_{entity_id}"
            
            hue_offset_schema[vol.Optional(field_name, default=hue_offsets.get(entity_id, 0.0))] = selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=-180.0,
                    max=180.0,
                    step=1.0,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="°"
                )
            )

        # If no colorable entities, skip this step
        if not hue_offset_schema:
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data={
                    "entities": self._entities,
                    "hue_offsets": {},
                    CONF_PROPORTION_RESET: self._proportion_reset,
                    CONF_RESET_TIMEOUT: self._reset_timeout,
                }
            )
            return self.async_create_entry(title="", data={})

        schema = vol.Schema(hue_offset_schema)
        
        return self.async_show_form(
            step_id="colors",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "info": "Optional: Add personality to your lights with per-light hue adjustments. Leave at 0° for no adjustment."
            }
        )
