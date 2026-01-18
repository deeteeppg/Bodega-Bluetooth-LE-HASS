"""Exceptions for the Bodega BLE integration."""

from __future__ import annotations

from homeassistant.exceptions import HomeAssistantError


class BodegaBleError(HomeAssistantError):
    """Base exception for Bodega BLE integration."""

    translation_domain = "bodega_ble"


class BodegaBleConnectionError(BodegaBleError):
    """Error connecting to Bodega BLE device."""

    translation_key = "connection_failed"


class BodegaBleMissingDataError(BodegaBleError):
    """Error when required data is missing for a command."""

    translation_key = "missing_data"


class BodegaBleCommandError(BodegaBleError):
    """Error sending command to Bodega BLE device."""

    translation_key = "command_failed"


class BodegaBleTimeoutError(BodegaBleError):
    """Timeout communicating with Bodega BLE device."""

    translation_key = "timeout"
