"""Tests for setup/unload behavior."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.bodega_ble import async_setup_entry, async_unload_entry
from custom_components.bodega_ble.const import DOMAIN

pytestmark = pytest.mark.asyncio


async def test_setup_and_unload_entry_resilient(hass, mock_config_entry) -> None:
    """Test setup succeeds even when the BLE device is not found."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.bodega_ble.async_ble_device_from_address",
        return_value=None,
    ), patch(
        "custom_components.bodega_ble.BodegaBleCoordinator.async_start",
        return_value=lambda: None,
    ), patch(
        "custom_components.bodega_ble.BodegaBleCoordinator.async_config_entry_first_refresh",
        side_effect=UpdateFailed("Device not found"),
    ), patch.object(
        hass.config_entries,
        "async_forward_entry_setups",
        new=AsyncMock(return_value=True),
    ):
        assert await async_setup_entry(hass, mock_config_entry) is True

    assert mock_config_entry.entry_id in hass.data[DOMAIN]

    with patch.object(
        hass.config_entries,
        "async_unload_platforms",
        new=AsyncMock(return_value=True),
    ):
        assert await async_unload_entry(hass, mock_config_entry) is True

    assert mock_config_entry.entry_id not in hass.data.get(DOMAIN, {})
