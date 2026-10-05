"""Tests for the Intelbras iSIC config flow."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.helpers import config_validation
from probatio import to_field_list

from custom_components.intelbras_isic.config_flow import _schema
from custom_components.intelbras_isic.const import (
    CONF_CHANNELS,
    CONF_CLOUD_APP_KEY,
    CONF_CLOUD_P2P_PASSWORD,
    CONF_DEVICE_PASSWORD,
    CONF_DEVICE_USERNAME,
    CONF_PROFILE,
    CONF_RTSP_PORT,
    CONF_SERIAL,
    DOMAIN,
)
from custom_components.intelbras_isic.rtsp import RtspAuthError

USER_INPUT = {
    CONF_CLOUD_APP_KEY: "synthetic-application-key",
    CONF_CLOUD_P2P_PASSWORD: "synthetic-p2p-password",
    CONF_SERIAL: "TESTSERIAL1234",
    CONF_DEVICE_USERNAME: "admin",
    CONF_DEVICE_PASSWORD: "not-a-real-password",
    CONF_CHANNELS: 8,
    CONF_PROFILE: "1",
    CONF_RTSP_PORT: 554,
}


async def test_successful_user_flow(hass) -> None:
    """A working cloud tunnel and RTSP login create an entry."""
    with (
        patch(
            "custom_components.intelbras_isic.config_flow.BridgeManager.async_start",
            AsyncMock(return_value=12345),
        ),
        patch(
            "custom_components.intelbras_isic.config_flow.BridgeManager.async_stop",
            AsyncMock(),
        ),
        patch("custom_components.intelbras_isic.config_flow.async_probe", AsyncMock()),
        patch(
            "custom_components.intelbras_isic.async_setup_entry",
            AsyncMock(return_value=True),
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] is data_entry_flow.FlowResultType.FORM

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )

    assert result["type"] is data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Intelbras 1234"
    assert result["data"] == USER_INPUT


async def test_invalid_device_credentials(hass) -> None:
    """Rejected RTSP credentials keep the user in the form."""
    with (
        patch(
            "custom_components.intelbras_isic.config_flow.BridgeManager.async_start",
            AsyncMock(return_value=12345),
        ),
        patch(
            "custom_components.intelbras_isic.config_flow.BridgeManager.async_stop",
            AsyncMock(),
        ),
        patch(
            "custom_components.intelbras_isic.config_flow.async_probe",
            AsyncMock(side_effect=RtspAuthError("rejected")),
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )

    assert result["type"] is data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


def test_forms_serialize_for_the_home_assistant_frontend():
    fields = to_field_list(
        _schema({}, include_serial=True),
        custom_serializer=config_validation.custom_serializer,
    )
    secrets = {
        field["name"]: field
        for field in fields
        if field["name"] in (CONF_CLOUD_APP_KEY, CONF_CLOUD_P2P_PASSWORD)
    }
    assert len(secrets) == 2
    assert all(
        field["selector"]["text"]["type"] == "password" for field in secrets.values()
    )


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        (CONF_CLOUD_APP_KEY, "", "invalid_cloud_app_key"),
        (CONF_CLOUD_APP_KEY, "x" * 33, "invalid_cloud_app_key"),
        (CONF_CLOUD_APP_KEY, "non-ascii-é", "invalid_cloud_app_key"),
        (CONF_CLOUD_P2P_PASSWORD, "", "invalid_cloud_p2p_password"),
        (CONF_CLOUD_P2P_PASSWORD, "contains\0nul", "invalid_cloud_p2p_password"),
    ],
)
async def test_invalid_cloud_credentials_do_not_open_a_tunnel(
    hass, field, value, error
):
    with patch("custom_components.intelbras_isic.config_flow.BridgeManager") as bridge:
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={**USER_INPUT, field: value},
        )
    assert result["type"] is data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {field: error}
    bridge.assert_not_called()
