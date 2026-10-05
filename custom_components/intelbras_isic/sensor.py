"""Diagnostic sensors for Intelbras iSIC Cloud."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import IsicConfigEntry
from .const import CONF_CHANNELS, CONF_PROFILE, CONF_SERIAL
from .entity import IsicEntity


@dataclass(frozen=True, kw_only=True)
class IsicSensorDescription(SensorEntityDescription):
    """Describe an iSIC diagnostic sensor."""

    value_fn: Callable[[IsicConfigEntry], Any]


SENSORS = (
    IsicSensorDescription(
        key="tunnel_uptime",
        translation_key="tunnel_uptime",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda entry: entry.runtime_data.bridge.uptime_seconds,
    ),
    IsicSensorDescription(
        key="successful_starts",
        translation_key="successful_starts",
        value_fn=lambda entry: entry.runtime_data.bridge.successful_starts,
    ),
    IsicSensorDescription(
        key="configured_channels",
        translation_key="configured_channels",
        value_fn=lambda entry: entry.data[CONF_CHANNELS],
    ),
    IsicSensorDescription(
        key="stream_profile",
        translation_key="stream_profile",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda entry: (
            "substream_h264" if entry.data[CONF_PROFILE] == "1" else "mainstream_h265"
        ),
    ),
    IsicSensorDescription(
        key="local_port",
        translation_key="local_port",
        entity_registry_enabled_default=False,
        value_fn=lambda entry: entry.runtime_data.bridge.local_port,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: IsicConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up bridge diagnostic sensors."""
    async_add_entities(IsicSensor(entry, description) for description in SENSORS)


class IsicSensor(IsicEntity, SensorEntity):
    """Expose one piece of bridge runtime information."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = True

    def __init__(
        self, entry: IsicConfigEntry, description: IsicSensorDescription
    ) -> None:
        super().__init__(entry)
        self.entity_description = description
        self._attr_unique_id = f"{entry.data[CONF_SERIAL]}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the current diagnostic value."""
        return self.entity_description.value_fn(self._entry)

    @property
    def options(self) -> list[str] | None:
        """Return the translated enum options when applicable."""
        if self.entity_description.key == "stream_profile":
            return ["substream_h264", "mainstream_h265"]
        return None
