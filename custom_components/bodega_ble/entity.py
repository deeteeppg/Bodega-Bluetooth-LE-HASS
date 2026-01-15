"""Shared entity helpers for the Bodega BLE integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo

from .const import DOMAIN


def device_info_for_entry(entry) -> DeviceInfo:
    """Return DeviceInfo for a config entry."""
    address = entry.data["address"]
    return DeviceInfo(
        identifiers={(DOMAIN, address)},
        connections={(CONNECTION_BLUETOOTH, address)},
        name=entry.title,
        manufacturer="DeeTeePPG",
        model="BLE Fridge",
    )
