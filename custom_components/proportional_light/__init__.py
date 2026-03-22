from __future__ import annotations

from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from . import ws_api

PLATFORMS: list[Platform] = [Platform.LIGHT]

# Path to the built frontend bundle
_PANEL_URL = f"/{DOMAIN}/panel.js"
_PANEL_DIR = Path(__file__).parent / "www"
_PANEL_COMPONENT = "proportional-light-panel"
_PANEL_PATH = "proportional-light"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:  # noqa: ARG001
    """
    One-time integration setup.

    - Registers the built frontend bundle as a static HTTP path so the
      browser can load it.
    - Registers a sidebar panel that uses the bundle.
    - Registers custom WebSocket commands used by the panel.
    """
    # Serve the built JS bundle
    hass.http.register_static_path(_PANEL_URL, str(_PANEL_DIR / "panel.js"), cache_headers=False)

    # Register a sidebar panel (only once — HA deduplicates by frontend_url_path)
    from homeassistant.components import panel_custom  # local import to avoid circular deps

    await panel_custom.async_register_panel(
        hass,
        component_name=_PANEL_COMPONENT,
        sidebar_title="Proportional Light",
        sidebar_icon="mdi:lightbulb-group",
        frontend_url_path=_PANEL_PATH,
        module_url=_PANEL_URL,
        require_admin=True,
        embed_iframe=False,
        trust_external_script=False,
    )

    # Register WebSocket API commands
    ws_api.async_register_commands(hass)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
