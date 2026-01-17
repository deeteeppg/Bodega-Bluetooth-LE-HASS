"""Diagnostics support for Bodega BLE."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

# Keys to redact from diagnostics output
TO_REDACT = {"address", "unique_id"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)

    # Redact the Bluetooth MAC address for privacy
    redacted_data = async_redact_data(dict(entry.data), TO_REDACT)

    diagnostics_data: dict[str, Any] = {
        "entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "domain": entry.domain,
            "title": entry.title,
            "data": redacted_data,
            "options": dict(entry.options),
        },
    }

    if coordinator:
        # Include coordinator state with address redacted
        coordinator_data = coordinator.data or {}

        diagnostics_data["coordinator"] = {
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
            "data": coordinator_data,
        }

        # Add BLE connection info
        diagnostics_data["ble"] = {
            "address": "**REDACTED**",
            "last_seen": (
                coordinator._last_seen.isoformat()
                if coordinator._last_seen
                else None
            ),
            "backoff_step": coordinator._backoff_step,
            "device_available": coordinator._ble_device is not None,
        }

    return diagnostics_data
