from __future__ import annotations

import logging
from pathlib import Path

from aiohttp import web
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, LOGGER_NAME
from . import ws_api

_LOGGER = logging.getLogger(LOGGER_NAME)

PLATFORMS: list[Platform] = [Platform.LIGHT]

_PANEL_URL = "/proportional_light/panel.js"
_PANEL_DIR = Path(__file__).parent / "www"
_PANEL_COMPONENT = "proportional-light-panel"
_PANEL_PATH = "proportional-light"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:  # noqa: ARG001
    """
    One-time integration setup.

    - Serves the frontend bundle as a static file
    - Registers a sidebar panel
    - Registers WebSocket API commands
    """
    # Serve the built JS bundle
    async def serve_panel(request: web.Request) -> web.FileResponse:
        file_path = _PANEL_DIR / "panel.js"
        return web.FileResponse(file_path)

    hass.http.app.router.add_get(_PANEL_URL, serve_panel)

    # Register the sidebar panel
    from homeassistant.components import panel_custom

    try:
        await panel_custom.async_register_panel(
            hass,
            component_name=_PANEL_COMPONENT,
            sidebar_title="Proportional Light",
            sidebar_icon="mdi:lightbulb-group",
            frontend_url_path=_PANEL_PATH,
            module_url=_PANEL_URL,
            require_admin=True,
            embed_iframe=False,
        )
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Failed to register panel: %s", err)

    # Register WebSocket API commands
    ws_api.async_register_commands(hass)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
