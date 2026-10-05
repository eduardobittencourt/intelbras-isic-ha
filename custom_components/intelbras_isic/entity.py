"""Shared entities for Intelbras iSIC Cloud."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from . import IsicConfigEntry
from .const import CONF_SERIAL, DOMAIN


class IsicEntity(Entity):
    """Base class for entities that belong to an iSIC config entry."""

    _attr_has_entity_name = True

    def __init__(self, entry: IsicConfigEntry) -> None:
        super().__init__()
        self._entry = entry
        serial = entry.data[CONF_SERIAL]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer="Intelbras",
            model="iSIC cloud recorder",
            name=entry.title,
        )
