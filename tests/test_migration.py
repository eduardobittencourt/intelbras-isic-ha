"""Upgrade private-preview entries without losing devices or leaking secrets."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.exceptions import ConfigEntryAuthFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.intelbras_isic import async_migrate_entry, async_setup_entry
from custom_components.intelbras_isic.const import (
    CONF_CLOUD_APP_KEY,
    CONF_CLOUD_P2P_PASSWORD,
    CONF_SERIAL,
    DOMAIN,
)

from .test_config_flow import USER_INPUT


def _old_entry():
    data = {
        key: value
        for key, value in USER_INPUT.items()
        if key not in (CONF_CLOUD_APP_KEY, CONF_CLOUD_P2P_PASSWORD)
    }
    return MockConfigEntry(
        domain=DOMAIN,
        version=1,
        unique_id=data[CONF_SERIAL],
        title="Existing recorder",
        data=data,
    )


async def test_migrate_keeps_device_identity_and_requests_credentials(hass):
    entry = _old_entry()
    entry.add_to_hass(hass)
    before = dict(entry.data)
    identifier = entry.entry_id
    assert await async_migrate_entry(hass, entry)
    assert entry.version == 2
    assert entry.entry_id == identifier
    assert entry.unique_id == before[CONF_SERIAL]
    assert entry.data == before
    with (
        patch("custom_components.intelbras_isic.BridgeManager") as bridge,
        pytest.raises(ConfigEntryAuthFailed) as raised,
    ):
        await async_setup_entry(hass, entry)
    bridge.assert_not_called()
    assert raised.value.translation_key == "missing_cloud_credentials"


@pytest.mark.parametrize("source", ["reauth", "reconfigure"])
async def test_existing_flow_updates_credentials_in_place(hass, source):
    entry = _old_entry()
    entry.add_to_hass(hass)
    identifier = entry.entry_id
    data = {key: value for key, value in USER_INPUT.items() if key != CONF_SERIAL}
    with (
        patch(
            "custom_components.intelbras_isic.config_flow._async_validate",
            AsyncMock(return_value={}),
        ) as validate,
        patch.object(hass.config_entries, "async_schedule_reload") as reload_entry,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": source, "entry_id": identifier},
            data=dict(entry.data) if source == "reauth" else None,
        )
        assert result["type"] is data_entry_flow.FlowResultType.FORM
        result = await hass.config_entries.flow.async_configure(result["flow_id"], data)
    assert result["type"] is data_entry_flow.FlowResultType.ABORT
    assert result["reason"] == f"{source}_successful"
    assert entry.entry_id == identifier
    assert entry.unique_id == USER_INPUT[CONF_SERIAL]
    assert entry.data == USER_INPUT
    validate.assert_awaited_once_with(USER_INPUT)
    reload_entry.assert_called_once_with(identifier)


async def test_duplicate_serial_does_not_open_another_tunnel(hass):
    entry = _old_entry()
    entry.add_to_hass(hass)
    with patch(
        "custom_components.intelbras_isic.config_flow._async_validate", AsyncMock()
    ) as validate:
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}, data=USER_INPUT
        )
    assert result["reason"] == "already_configured"
    validate.assert_not_awaited()
