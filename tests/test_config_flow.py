"""Tests for the config flow."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from homeassistant import config_entries
from homeassistant.const import CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResultType

from custom_components.bodega_ble.const import DOMAIN

pytestmark = pytest.mark.asyncio


async def test_user_flow_manual_address(hass) -> None:
    """Test manual address entry when no devices are discovered."""
    with patch(
        "custom_components.bodega_ble.config_flow.async_discovered_service_info",
        return_value=[],
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_ADDRESS: "AA:BB:CC:DD:EE:FF"},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"].startswith("Bodega BLE Fridge")
    assert result["data"] == {CONF_ADDRESS: "AA:BB:CC:DD:EE:FF"}


async def test_user_flow_invalid_address(hass) -> None:
    """Test invalid address handling."""
    with patch(
        "custom_components.bodega_ble.config_flow.async_discovered_service_info",
        return_value=[],
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_ADDRESS: "BAD"},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_address"}
