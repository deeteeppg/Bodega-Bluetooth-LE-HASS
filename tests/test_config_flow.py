"""Tests for the Bodega BLE config flow."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.bodega_ble.const import DOMAIN, SERVICE_UUID


@pytest.fixture
def mock_discovery_info() -> BluetoothServiceInfoBleak:
    """Create a mock BluetoothServiceInfoBleak."""
    return BluetoothServiceInfoBleak(
        name="AK1-TEST123",
        address="AA:BB:CC:DD:EE:FF",
        rssi=-60,
        manufacturer_data={},
        service_data={},
        service_uuids=[SERVICE_UUID],
        source="local",
        device=MagicMock(),
        advertisement=MagicMock(),
        connectable=True,
        time=0,
        tx_power=None,
    )


class TestBodegaBleConfigFlow:
    """Tests for the config flow."""

    async def test_user_flow_valid_address(self, hass: HomeAssistant) -> None:
        """Test user flow with valid address."""
        with patch(
            "custom_components.bodega_ble.async_setup_entry",
            return_value=True,
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )
            assert result["type"] == FlowResultType.FORM
            assert result["step_id"] == "user"

            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                {CONF_ADDRESS: "AA:BB:CC:DD:EE:FF"},
            )
            assert result["type"] == FlowResultType.CREATE_ENTRY
            assert result["data"][CONF_ADDRESS] == "AA:BB:CC:DD:EE:FF"

    async def test_user_flow_invalid_address(self, hass: HomeAssistant) -> None:
        """Test user flow with invalid address format."""
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_ADDRESS: "invalid"},
        )
        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"base": "invalid_address"}

    async def test_bluetooth_discovery(
        self, hass: HomeAssistant, mock_discovery_info: BluetoothServiceInfoBleak
    ) -> None:
        """Test Bluetooth discovery flow."""
        with patch(
            "custom_components.bodega_ble.async_setup_entry",
            return_value=True,
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": config_entries.SOURCE_BLUETOOTH},
                data=mock_discovery_info,
            )
            assert result["type"] == FlowResultType.FORM
            assert result["step_id"] == "bluetooth_confirm"

            result = await hass.config_entries.flow.async_configure(
                result["flow_id"], {}
            )
            assert result["type"] == FlowResultType.CREATE_ENTRY
            assert result["title"] == "AK1-TEST123"

    async def test_bluetooth_discovery_unsupported_device(
        self, hass: HomeAssistant
    ) -> None:
        """Test Bluetooth discovery with unsupported device."""
        discovery_info = BluetoothServiceInfoBleak(
            name="SomeOtherDevice",
            address="AA:BB:CC:DD:EE:FF",
            rssi=-60,
            manufacturer_data={},
            service_data={},
            service_uuids=[],
            source="local",
            device=MagicMock(),
            advertisement=MagicMock(),
            connectable=True,
            time=0,
            tx_power=None,
        )

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_BLUETOOTH},
            data=discovery_info,
        )
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "not_supported"

    async def test_duplicate_entry(
        self, hass: HomeAssistant, mock_config_entry
    ) -> None:
        """Test that duplicate entries are rejected."""
        mock_config_entry.add_to_hass(hass)

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_ADDRESS: "AA:BB:CC:DD:EE:FF"},
        )
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "already_configured"
