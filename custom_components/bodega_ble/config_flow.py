"""Config flow for Bodega BLE integration.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS

from .const import DEVICE_NAME_PREFIXES, DOMAIN, NAME, SERVICE_UUID


class BodegaBleConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bodega BLE devices."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: dict[str, str] = {}
        self._discovered_info: BluetoothServiceInfoBleak | None = None

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle a Bluetooth discovery."""
        if not self._is_supported_device(discovery_info):
            return self.async_abort(reason="not_supported")

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self._discovered_info = discovery_info
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm Bluetooth device setup."""
        if user_input is not None and self._discovered_info:
            discovery_info = self._discovered_info
            title = discovery_info.name or f"{NAME} {discovery_info.address[-8:]}"
            return self.async_create_entry(
                title=title,
                data={
                    CONF_ADDRESS: discovery_info.address,
                },
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={
                "name": self._discovered_info.name if self._discovered_info else NAME
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle user-initiated config flow."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS]

            if not self._is_valid_address(address):
                errors["base"] = "invalid_address"
            else:
                await self.async_set_unique_id(address)
                self._abort_if_unique_id_configured()

                title = self._discovered_devices.get(
                    address, f"{NAME} {address[-8:]}"
                )

                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_ADDRESS: address,
                    },
                )

        discovered = await self._async_get_discovered_devices()
        discovered_list = ", ".join(
            f"{name} ({address})" for address, name in discovered.items()
        )
        discovered_text = (
            discovered_list if discovered_list else "No BLE devices discovered yet."
        )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): str,
                }
            ),
            errors=errors,
            description_placeholders={"discovered": discovered_text},
        )

    async def _async_get_discovered_devices(self) -> dict[str, str]:
        """Get discovered Bluetooth devices."""
        devices: dict[str, str] = {}

        for discovery_info in async_discovered_service_info(self.hass):
            if not self._is_supported_device(discovery_info):
                continue
            if discovery_info.address in self._async_current_ids():
                continue

            display_name = (
                discovery_info.name
                or f"Unknown ({discovery_info.address[-8:]})"
            )
            devices[discovery_info.address] = display_name

        self._discovered_devices = devices
        return self._discovered_devices

    def _is_valid_address(self, address: str) -> bool:
        """Validate Bluetooth address format."""
        parts = address.upper().split(":")
        if len(parts) != 6:
            return False
        return all(
            len(part) == 2 and all(c in "0123456789ABCDEF" for c in part)
            for part in parts
        )

    def _is_supported_device(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> bool:
        """Check if the discovered device is supported."""
        if discovery_info.name and discovery_info.name.startswith(
            DEVICE_NAME_PREFIXES
        ):
            return True
        if SERVICE_UUID in discovery_info.service_uuids:
            return True
        return False
