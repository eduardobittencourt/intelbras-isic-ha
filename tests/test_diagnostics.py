"""Tests for privacy-safe diagnostics."""

from types import SimpleNamespace

from custom_components.intelbras_isic.const import (
    CONF_CHANNELS,
    CONF_CLOUD_APP_KEY,
    CONF_CLOUD_P2P_PASSWORD,
    CONF_DEVICE_PASSWORD,
    CONF_DEVICE_USERNAME,
    CONF_SERIAL,
)
from custom_components.intelbras_isic.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_diagnostics_redact_credentials(hass) -> None:
    """Diagnostics never expose the serial or RTSP credentials."""
    bridge = SimpleNamespace(
        ready=True,
        started_at=None,
        uptime_seconds=12,
        successful_starts=1,
        last_error=None,
    )
    entry = SimpleNamespace(
        data={
            CONF_CLOUD_APP_KEY: "SECRET-CLOUD-KEY",
            CONF_CLOUD_P2P_PASSWORD: "SECRET-CLOUD-PASSWORD",
            CONF_SERIAL: "SECRET-SERIAL",
            CONF_DEVICE_USERNAME: "SECRET-USER",
            CONF_DEVICE_PASSWORD: "SECRET-PASSWORD",
            CONF_CHANNELS: 8,
        },
        runtime_data=SimpleNamespace(bridge=bridge),
    )

    result = await async_get_config_entry_diagnostics(hass, entry)

    rendered = str(result)
    assert "SECRET-SERIAL" not in rendered
    assert "SECRET-USER" not in rendered
    assert "SECRET-PASSWORD" not in rendered
    assert "SECRET-CLOUD" not in rendered
    assert result["config_entry"][CONF_CHANNELS] == 8
