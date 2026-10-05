"""Diagnostic binary sensors for Intelbras iSIC Cloud."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import IsicConfigEntry
from .const import CONF_SERIAL
from .entity import IsicEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: IsicConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up bridge connectivity diagnostics."""
    async_add_entities([IsicTunnelBinarySensor(entry)])


class IsicTunnelBinarySensor(IsicEntity, BinarySensorEntity):
    """Report whether the P2P tunnel process is ready."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = True
    _attr_translation_key = "tunnel"

    def __init__(self, entry: IsicConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.data[CONF_SERIAL]}_tunnel"

    @property
    def is_on(self) -> bool:
        """Return whether the bridge is running and has a local tunnel."""
        return self._entry.runtime_data.bridge.ready
