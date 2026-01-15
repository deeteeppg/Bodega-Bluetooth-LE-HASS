"""Bodega BLE Integration.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home

This integration provides BLE control + telemetry for Bodega fridges.
"""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components.bluetooth import (
    async_ble_device_from_address,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    SERVICE_SET_BATTERY_SAVER,
    SERVICE_SET_LEFT_TARGET,
    SERVICE_SET_LOCK,
    SERVICE_SET_POWER,
    SERVICE_SET_RIGHT_TARGET,
    SERVICE_SET_RUN_MODE,
)
from .coordinator import BodegaBleCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]

type BodegaBleConfigEntry = ConfigEntry[BodegaBleCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: BodegaBleConfigEntry
) -> bool:
    """Set up Bluetooth device from a config entry."""
    address: str = entry.data["address"]

    # Get the BLE device from Home Assistant's Bluetooth manager
    ble_device = async_ble_device_from_address(
        hass, address, connectable=True
    )

    if not ble_device:
        _LOGGER.warning(
            "Bluetooth device %s not found during setup; will retry in background",
            address,
        )

    # Create coordinator
    coordinator = BodegaBleCoordinator(hass, entry, ble_device)

    # Start listening for advertisements
    entry.async_on_unload(coordinator.async_start())

    # Initial data fetch
    try:
        await coordinator.async_config_entry_first_refresh()
    except (ConfigEntryNotReady, UpdateFailed) as err:
        _LOGGER.warning("Initial BLE refresh failed: %s", err)

    entry.runtime_data = coordinator
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _register_services(hass)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: BodegaBleConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok and DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


def _register_services(
    hass: HomeAssistant,
) -> None:
    """Register integration services."""
    if hass.services.has_service(DOMAIN, SERVICE_SET_LEFT_TARGET):
        return

    async def _get_coordinator(entry_id: str) -> BodegaBleCoordinator:
        coordinator = hass.data.get(DOMAIN, {}).get(entry_id)
        if not coordinator:
            raise HomeAssistantError(f"Unknown entry_id: {entry_id}")
        return coordinator

    async def _handle_set_left_target(call) -> None:
        coordinator = await _get_coordinator(call.data["entry_id"])
        await coordinator.async_set_left_target(call.data["temperature"])
        await coordinator.async_request_refresh()

    async def _handle_set_right_target(call) -> None:
        coordinator = await _get_coordinator(call.data["entry_id"])
        await coordinator.async_set_right_target(call.data["temperature"])
        await coordinator.async_request_refresh()

    async def _handle_set_power(call) -> None:
        coordinator = await _get_coordinator(call.data["entry_id"])
        await coordinator.async_set_power(call.data["powered"])
        await coordinator.async_request_refresh()

    async def _handle_set_lock(call) -> None:
        coordinator = await _get_coordinator(call.data["entry_id"])
        await coordinator.async_set_lock(call.data["locked"])
        await coordinator.async_request_refresh()

    async def _handle_set_run_mode(call) -> None:
        coordinator = await _get_coordinator(call.data["entry_id"])
        await coordinator.async_set_run_mode(call.data["mode"])
        await coordinator.async_request_refresh()

    async def _handle_set_battery_saver(call) -> None:
        coordinator = await _get_coordinator(call.data["entry_id"])
        await coordinator.async_set_battery_saver(call.data["level"])
        await coordinator.async_request_refresh()

    services = [
        (
            SERVICE_SET_LEFT_TARGET,
            _handle_set_left_target,
            vol.Schema(
                {
                    vol.Required("entry_id"): cv.string,
                    vol.Required("temperature"): vol.Coerce(float),
                }
            ),
        ),
        (
            SERVICE_SET_RIGHT_TARGET,
            _handle_set_right_target,
            vol.Schema(
                {
                    vol.Required("entry_id"): cv.string,
                    vol.Required("temperature"): vol.Coerce(float),
                }
            ),
        ),
        (
            SERVICE_SET_POWER,
            _handle_set_power,
            vol.Schema(
                {
                    vol.Required("entry_id"): cv.string,
                    vol.Required("powered"): cv.boolean,
                }
            ),
        ),
        (
            SERVICE_SET_LOCK,
            _handle_set_lock,
            vol.Schema(
                {
                    vol.Required("entry_id"): cv.string,
                    vol.Required("locked"): cv.boolean,
                }
            ),
        ),
        (
            SERVICE_SET_RUN_MODE,
            _handle_set_run_mode,
            vol.Schema(
                {
                    vol.Required("entry_id"): cv.string,
                    vol.Required("mode"): cv.string,
                }
            ),
        ),
        (
            SERVICE_SET_BATTERY_SAVER,
            _handle_set_battery_saver,
            vol.Schema(
                {
                    vol.Required("entry_id"): cv.string,
                    vol.Required("level"): cv.string,
                }
            ),
        ),
    ]

    for service_name, handler, schema in services:
        if hass.services.has_service(DOMAIN, service_name):
            continue
        hass.services.async_register(DOMAIN, service_name, handler, schema=schema)
