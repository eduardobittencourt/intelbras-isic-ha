"""Configure device authentication and separately supplied Cloud credentials."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .bridge import BridgeError, BridgeManager
from .const import (
    CONF_CHANNELS,
    CONF_CLOUD_APP_KEY,
    CONF_CLOUD_P2P_PASSWORD,
    CONF_DEVICE_PASSWORD,
    CONF_DEVICE_USERNAME,
    CONF_PROFILE,
    CONF_RTSP_PORT,
    CONF_SERIAL,
    DEFAULT_CHANNELS,
    DEFAULT_PROFILE,
    DEFAULT_RTSP_PORT,
    DOMAIN,
)
from .rtsp import RtspAuthError, RtspError, async_probe


def _schema(defaults: dict[str, Any], *, include_serial: bool) -> vol.Schema:
    password = selector.TextSelector(
        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
    )
    fields: dict[Any, Any] = {}
    if include_serial:
        fields[vol.Required(CONF_SERIAL)] = vol.All(
            str, vol.Strip, vol.Length(min=1, max=99)
        )
    fields.update(
        {
            vol.Required(
                CONF_DEVICE_USERNAME,
                default=defaults.get(CONF_DEVICE_USERNAME, "admin"),
            ): vol.All(str, vol.Length(min=1)),
            vol.Required(
                CONF_DEVICE_PASSWORD,
                default=defaults.get(CONF_DEVICE_PASSWORD, ""),
            ): password,
            vol.Required(
                CONF_CHANNELS, default=defaults.get(CONF_CHANNELS, DEFAULT_CHANNELS)
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=32)),
            vol.Required(
                CONF_PROFILE, default=defaults.get(CONF_PROFILE, DEFAULT_PROFILE)
            ): vol.In({"1": "Substream (H.264)", "0": "Main stream (H.265)"}),
            vol.Required(
                CONF_RTSP_PORT, default=defaults.get(CONF_RTSP_PORT, DEFAULT_RTSP_PORT)
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
            vol.Required(
                CONF_CLOUD_APP_KEY, default=defaults.get(CONF_CLOUD_APP_KEY, "")
            ): password,
            vol.Required(
                CONF_CLOUD_P2P_PASSWORD,
                default=defaults.get(CONF_CLOUD_P2P_PASSWORD, ""),
            ): password,
        }
    )
    return vol.Schema(fields)


async def _async_validate(data: dict[str, Any]) -> dict[str, str]:
    errors = {}
    for field, maximum, error in (
        (CONF_SERIAL, 99, "invalid_serial"),
        (CONF_CLOUD_APP_KEY, 32, "invalid_cloud_app_key"),
        (CONF_CLOUD_P2P_PASSWORD, None, "invalid_cloud_p2p_password"),
    ):
        value = data[field]
        if (
            not value
            or not value.isascii()
            or "\0" in value
            or (maximum is not None and len(value) > maximum)
        ):
            errors[field] = error
    if errors:
        return errors
    bridge = BridgeManager(
        data[CONF_SERIAL],
        data[CONF_RTSP_PORT],
        application_key=data[CONF_CLOUD_APP_KEY],
        p2p_password=data[CONF_CLOUD_P2P_PASSWORD],
    )
    try:
        port = await bridge.async_start()
        url = (
            f"rtsp://127.0.0.1:{port}/cam/realmonitor"
            f"?channel=1&subtype={data[CONF_PROFILE]}"
        )
        await async_probe(url, data[CONF_DEVICE_USERNAME], data[CONF_DEVICE_PASSWORD])
    except RtspAuthError:
        return {"base": "invalid_auth"}
    except (BridgeError, RtspError, OSError, TimeoutError):
        return {"base": "cannot_connect"}
    finally:
        await bridge.async_stop()
    return {}


class IsicConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure an Intelbras cloud device."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            data = _schema({}, include_serial=True)(user_input)
            await self.async_set_unique_id(data[CONF_SERIAL])
            self._abort_if_unique_id_configured()
            errors = await _async_validate(data)
            if not errors:
                return self.async_create_entry(
                    title=f"Intelbras {data[CONF_SERIAL][-4:]}", data=data
                )
        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input or {}, include_serial=True),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:
        """Prompt existing installations for credentials without recreating entities."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return await self._async_existing("reauth_confirm", user_input)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return await self._async_existing("reconfigure", user_input)

    async def _async_existing(
        self, step_id: str, user_input: dict[str, Any] | None
    ) -> FlowResult:
        entry = (
            self._get_reauth_entry()
            if step_id == "reauth_confirm"
            else self._get_reconfigure_entry()
        )
        defaults = dict(entry.data)
        errors: dict[str, str] = {}
        if user_input is not None:
            data = {
                **defaults,
                **_schema(defaults, include_serial=False)(user_input),
            }
            errors = await _async_validate(data)
            if not errors:
                return self.async_update_reload_and_abort(entry, data=data)
            defaults.update(user_input)
        return self.async_show_form(
            step_id=step_id,
            data_schema=_schema(defaults, include_serial=False),
            errors=errors,
        )
