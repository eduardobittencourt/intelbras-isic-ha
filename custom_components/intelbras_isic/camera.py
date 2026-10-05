"""Camera entities provided through the iSIC cloud tunnel."""

from __future__ import annotations

from urllib.parse import quote

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.components.ffmpeg import async_get_image
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import IsicConfigEntry, stream_url
from .const import (
    CONF_CHANNELS,
    CONF_DEVICE_PASSWORD,
    CONF_DEVICE_USERNAME,
    CONF_SERIAL,
)
from .entity import IsicEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: IsicConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Create one camera entity per configured recorder channel."""
    async_add_entities(
        IsicCamera(entry, channel)
        for channel in range(1, entry.data[CONF_CHANNELS] + 1)
    )


class IsicCamera(IsicEntity, Camera):
    """An RTSP camera reached through Intelbras P2P cloud."""

    _attr_has_entity_name = True
    _attr_supported_features = CameraEntityFeature.STREAM
    _attr_use_stream_for_stills = True

    def __init__(self, entry: IsicConfigEntry, channel: int) -> None:
        IsicEntity.__init__(self, entry)
        self._channel = channel
        serial = entry.data[CONF_SERIAL]
        self._attr_unique_id = f"{serial}_channel_{channel}"
        self._attr_name = f"Canal {channel}"

    @property
    def available(self) -> bool:
        """Return whether the Python tunnel is running."""
        return self._entry.runtime_data.bridge.ready

    async def stream_source(self) -> str | None:
        """Return an authenticated RTSP URL for Home Assistant's stream worker."""
        port = await self._entry.runtime_data.bridge.async_start()
        bare_url = stream_url(self._entry, port, self._channel)
        username = quote(self._entry.data[CONF_DEVICE_USERNAME], safe="")
        password = quote(self._entry.data[CONF_DEVICE_PASSWORD], safe="")
        return bare_url.replace("rtsp://", f"rtsp://{username}:{password}@", 1)

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a JPEG still generated from the H.264 stream."""
        source = await self.stream_source()
        if source is None:
            return None
        return await async_get_image(
            self.hass,
            f"-rtsp_transport tcp -i {source}",
            width=width,
            height=height,
        )
