"""
Resolve a SelectorConfig (area / device / entities) to a concrete list of
entity IDs and optionally subscribe to registry changes so the caller is
notified when the resolved set changes.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable

from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
)

from .const import LOGGER_NAME

_LOGGER = logging.getLogger(LOGGER_NAME)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SelectorConfig:
    """Describes how a proportional light group selects its members."""

    selector_type: str  # "entities" | "area" | "device"
    selector_value: str | list[str]  # area_id / device_id / [entity_id, ...]

    @classmethod
    def from_entry_data(cls, data: dict) -> "SelectorConfig":
        """
        Build a SelectorConfig from a config entry data dict.
        Supports the old 'entities' flat list as well as the new selector model.
        """
        if "selector_type" in data:
            return cls(
                selector_type=data["selector_type"],
                selector_value=data["selector_value"],
            )
        # Backward compat: plain list of entity_ids
        return cls(
            selector_type="entities",
            selector_value=data.get("entities", []),
        )


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


def resolve_selector(hass: HomeAssistant, config: SelectorConfig) -> list[str]:
    """
    Return the list of light entity IDs described by *config*.

    This is a synchronous helper that reads the current HA registries; it
    should be called from within the event loop (not from a thread).
    """
    selector_type = config.selector_type
    value = config.selector_value

    if selector_type == "entities":
        entities = value if isinstance(value, list) else [value]
        # Filter out any entities that no longer exist
        return [e for e in entities if hass.states.get(e) is not None or _entity_exists(hass, e)]

    ent_reg = er.async_get(hass)

    if selector_type == "area":
        area_id = value if isinstance(value, str) else (value[0] if value else "")
        entries = er.async_entries_for_area(ent_reg, area_id)
        return [
            entry.entity_id
            for entry in entries
            if entry.domain == LIGHT_DOMAIN and not entry.disabled_by
        ]

    if selector_type == "device":
        device_id = value if isinstance(value, str) else (value[0] if value else "")
        entries = er.async_entries_for_device(ent_reg, device_id)
        return [
            entry.entity_id
            for entry in entries
            if entry.domain == LIGHT_DOMAIN and not entry.disabled_by
        ]

    _LOGGER.warning("Unknown selector_type '%s', returning empty list", selector_type)
    return []


def _entity_exists(hass: HomeAssistant, entity_id: str) -> bool:
    """Return True if the entity exists in the entity registry (even if unavailable)."""
    ent_reg = er.async_get(hass)
    return ent_reg.async_get(entity_id) is not None


# ---------------------------------------------------------------------------
# Change subscription
# ---------------------------------------------------------------------------


def subscribe_selector_changes(
    hass: HomeAssistant,
    config: SelectorConfig,
    on_change: Callable[[], None],
) -> Callable[[], None]:
    """
    Listen to HA registry events that could change what *config* resolves to.

    Returns an unsubscribe callable.

    For selector_type == "entities", this is a no-op (the entity list is
    static; the coordinator handles entity state changes separately).
    For "area" and "device", we subscribe to registry-updated events.
    """
    unsubs: list[Callable[[], None]] = []

    if config.selector_type == "entities":
        # Static list — no registry watching needed
        return lambda: None

    @callback
    def _on_entity_registry_updated(event) -> None:
        action = event.data.get("action")
        if action not in ("create", "remove", "update"):
            return
        # Only react if a light entity in our area/device changed
        entity_id: str = event.data.get("entity_id", "")
        ent_reg = er.async_get(hass)
        entry = ent_reg.async_get(entity_id)
        if entry is None or entry.domain != LIGHT_DOMAIN:
            return

        if config.selector_type == "area":
            area_id = config.selector_value if isinstance(config.selector_value, str) else ""
            if entry.area_id == area_id or action == "remove":
                _LOGGER.debug(
                    "Entity registry change affects area selector '%s', triggering update", area_id
                )
                on_change()

        elif config.selector_type == "device":
            device_id = config.selector_value if isinstance(config.selector_value, str) else ""
            if entry.device_id == device_id or action == "remove":
                _LOGGER.debug(
                    "Entity registry change affects device selector '%s', triggering update", device_id
                )
                on_change()

    unsubs.append(
        hass.bus.async_listen(er.EVENT_ENTITY_REGISTRY_UPDATED, _on_entity_registry_updated)
    )

    if config.selector_type == "area":
        @callback
        def _on_area_registry_updated(event) -> None:
            area_id = config.selector_value if isinstance(config.selector_value, str) else ""
            if event.data.get("area_id") == area_id:
                _LOGGER.debug("Area registry change for '%s', triggering update", area_id)
                on_change()

        unsubs.append(
            hass.bus.async_listen(ar.EVENT_AREA_REGISTRY_UPDATED, _on_area_registry_updated)
        )

    def _unsubscribe() -> None:
        for unsub in unsubs:
            unsub()

    return _unsubscribe
