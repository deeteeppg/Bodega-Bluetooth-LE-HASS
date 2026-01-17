"""Shared entity helpers for the Bodega BLE integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo

from .const import DOMAIN


def device_info_for_entry(entry) -> DeviceInfo:
    """Return DeviceInfo for a config entry."""
    address = entry.data["address"]
    name = entry.title or ""

    # Infer model from device name prefix
    model = "Portable Fridge"
    if name.startswith(("AK1-", "AK2-", "AK3-")):
        model = "Dual Zone Portable Fridge"
    elif name.startswith("WT-"):
        model = "Single Zone Portable Fridge"
    elif name.startswith("A1-"):
        model = "Compact Portable Fridge"

    return DeviceInfo(
        identifiers={(DOMAIN, address)},
        connections={(CONNECTION_BLUETOOTH, address)},
        name=entry.title,
        manufacturer="Bodega / Alpicool",
        model=model,
    )
