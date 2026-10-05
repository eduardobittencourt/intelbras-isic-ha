"""Diagnostics support for Intelbras iSIC Cloud."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import IsicConfigEntry
from .const import (
    CONF_CLOUD_APP_KEY,
    CONF_CLOUD_P2P_PASSWORD,
    CONF_DEVICE_PASSWORD,
    CONF_DEVICE_USERNAME,
    CONF_SERIAL,
)

TO_REDACT = {
    CONF_CLOUD_APP_KEY,
    CONF_CLOUD_P2P_PASSWORD,
    CONF_DEVICE_PASSWORD,
    CONF_DEVICE_USERNAME,
    CONF_SERIAL,
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: IsicConfigEntry
) -> dict[str, Any]:
    """Return privacy-safe diagnostics for a config entry."""
    bridge = entry.runtime_data.bridge
    return {
        "config_entry": async_redact_data(dict(entry.data), TO_REDACT),
        "bridge": {
            "ready": bridge.ready,
            "started_at": bridge.started_at.isoformat() if bridge.started_at else None,
            "uptime_seconds": bridge.uptime_seconds,
            "successful_starts": bridge.successful_starts,
            "last_error": bridge.last_error,
        },
    }
