"""Intelbras iSIC Cloud integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .bridge import BridgeError, BridgeManager
from .const import (
    CONF_CLOUD_APP_KEY,
    CONF_CLOUD_P2P_PASSWORD,
    CONF_DEVICE_PASSWORD,
    CONF_DEVICE_USERNAME,
    CONF_PROFILE,
    CONF_RTSP_PORT,
    CONF_SERIAL,
    DEFAULT_PROFILE,
    DEFAULT_RTSP_PORT,
)
from .rtsp import RtspAuthError, RtspError, async_probe

PLATFORMS = [Platform.BINARY_SENSOR, Platform.CAMERA, Platform.SENSOR]


@dataclass
class IsicRuntimeData:
    """Runtime state owned by a config entry."""

    bridge: BridgeManager


type IsicConfigEntry = ConfigEntry[IsicRuntimeData]


def stream_url(entry: ConfigEntry, local_port: int, channel: int) -> str:
    """Build a credential-free URL used for connection tests."""
    subtype = entry.data.get(CONF_PROFILE, DEFAULT_PROFILE)
    return (
        f"rtsp://127.0.0.1:{local_port}/cam/realmonitor"
        f"?channel={channel}&subtype={subtype}"
    )


async def async_setup_entry(hass: HomeAssistant, entry: IsicConfigEntry) -> bool:
    """Start the P2P tunnel and create camera entities."""
    if not entry.data.get(CONF_CLOUD_APP_KEY) or not entry.data.get(
        CONF_CLOUD_P2P_PASSWORD
    ):
        raise ConfigEntryAuthFailed(
            translation_domain="intelbras_isic",
            translation_key="missing_cloud_credentials",
        )
    bridge = BridgeManager(
        entry.data[CONF_SERIAL],
        entry.data.get(CONF_RTSP_PORT, DEFAULT_RTSP_PORT),
        application_key=entry.data[CONF_CLOUD_APP_KEY],
        p2p_password=entry.data[CONF_CLOUD_P2P_PASSWORD],
    )
    try:
        local_port = await bridge.async_start()
        await async_probe(
            stream_url(entry, local_port, 1),
            entry.data[CONF_DEVICE_USERNAME],
            entry.data[CONF_DEVICE_PASSWORD],
        )
    except RtspAuthError as err:
        await bridge.async_stop()
        raise ConfigEntryAuthFailed(str(err)) from err
    except (BridgeError, RtspError, OSError, TimeoutError) as err:
        await bridge.async_stop()
        raise ConfigEntryNotReady(str(err)) from err

    entry.runtime_data = IsicRuntimeData(bridge)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: IsicConfigEntry) -> bool:
    """Keep existing devices and entities when upgrading the private preview."""
    if entry.version > 2:
        return False
    if entry.version == 1:
        hass.config_entries.async_update_entry(entry, version=2, minor_version=1)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: IsicConfigEntry) -> bool:
    """Unload cameras and stop their P2P tunnel."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.bridge.async_stop()
    return unloaded
