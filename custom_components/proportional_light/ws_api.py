"""
WebSocket API commands exposed to the frontend panel.

Registration happens in async_setup() via:

    ws_api.async_register_commands(hass)
"""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, LOGGER_NAME
from .entity_resolver import SelectorConfig, resolve_selector

_LOGGER = logging.getLogger(LOGGER_NAME)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


@callback
def async_register_commands(hass: HomeAssistant) -> None:
    """Register all WS commands for the proportional_light domain."""
    websocket_api.async_register_command(hass, ws_get_resolved_entities)
    websocket_api.async_register_command(hass, ws_update_entry)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@websocket_api.websocket_command(
    {
        vol.Required("type"): "proportional_light/get_resolved_entities",
        vol.Required("entry_id"): str,
    }
)
@websocket_api.async_response
async def ws_get_resolved_entities(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """
    Return the list of entity IDs currently resolved for a config entry.

    This lets the frontend panel show which lights are actually tracked for
    area / device selectors without needing to replicate the resolution logic.
    """
    entry: ConfigEntry | None = hass.config_entries.async_get_entry(msg["entry_id"])
    if entry is None or entry.domain != DOMAIN:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Config entry not found")
        return

    config = SelectorConfig.from_entry_data(entry.data)

    try:
        entities = resolve_selector(hass, config)
    except Exception as exc:  # noqa: BLE001
        _LOGGER.exception("Failed to resolve selector for entry %s", entry.entry_id)
        connection.send_error(msg["id"], websocket_api.ERR_UNKNOWN_ERROR, str(exc))
        return

    connection.send_result(msg["id"], {"entities": entities})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "proportional_light/update_entry",
        vol.Required("entry_id"): str,
        vol.Required("data"): dict,
    }
)
@websocket_api.async_response
async def ws_update_entry(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """
    Update the config entry data from the frontend panel.

    The *data* payload must match the EntryData TypeScript interface:
    {
        "name": str,
        "selector_type": "entities" | "area" | "device",
        "selector_value": str | [str],
        "entity_props": { entity_id: { hue_offset?: float, default_proportion?: float } },
        "proportion_reset_mode": str,
        "proportion_reset_timeout": int,
    }
    """
    entry: ConfigEntry | None = hass.config_entries.async_get_entry(msg["entry_id"])
    if entry is None or entry.domain != DOMAIN:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Config entry not found")
        return

    new_data: dict = msg["data"]

    # Basic shape validation — full schema validation can be added later
    required_keys = {"name", "selector_type", "selector_value", "entity_props"}
    missing = required_keys - new_data.keys()
    if missing:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            f"Missing required fields: {missing}",
        )
        return

    if new_data["selector_type"] not in ("entities", "area", "device"):
        connection.send_error(
            msg["id"],
            websocket_api.ERR_INVALID_FORMAT,
            "selector_type must be one of: entities, area, device",
        )
        return

    # Merge into entry data and trigger a reload so the coordinator picks up changes
    merged = {**entry.data, **new_data}
    hass.config_entries.async_update_entry(entry, data=merged, title=new_data["name"])

    # Reload so coordinator re-resolves the selector and restarts state tracking
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True})
