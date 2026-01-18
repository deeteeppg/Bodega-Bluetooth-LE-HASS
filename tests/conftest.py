"""Fixtures for bodega_ble tests."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.bodega_ble.const import DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for tests."""
    yield


@pytest.fixture
def enable_bluetooth() -> None:
    """Fixture to enable bluetooth mocking."""
    from unittest.mock import MagicMock

    mock_manager = MagicMock()
    mock_manager.async_discovered_service_info = MagicMock(return_value=[])

    with (
        patch(
            "homeassistant.components.bluetooth.async_setup",
            return_value=True,
        ),
        patch(
            "homeassistant.components.bluetooth.async_setup_entry",
            return_value=True,
        ),
        patch(
            "homeassistant.components.bluetooth.async_get_bluetooth",
            return_value=mock_manager,
        ),
        patch(
            "homeassistant.components.bluetooth.async_discovered_service_info",
            return_value=[],
        ),
        patch(
            "habluetooth.central_manager.get_manager",
            return_value=mock_manager,
        ),
        patch(
            "custom_components.bodega_ble.config_flow.async_discovered_service_info",
            return_value=[],
        ),
    ):
        yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test Fridge",
        data={"address": "AA:BB:CC:DD:EE:FF"},
        unique_id="AA:BB:CC:DD:EE:FF",
    )


@pytest.fixture
def valid_notify_payload_single_zone() -> bytes:
    """Return a valid single-zone notify payload."""
    data = bytes(
        [
            0x00,  # locked = False
            0x01,  # powered = True
            0x00,  # run_mode = Max
            0x01,  # battery_saver = Mid
            0x05,  # left_target = 5C
            0x0A,  # temp_max = 10C
            0x00,  # temp_min = 0C
            0x02,  # left_ret_diff = 2
            0x03,  # start_delay = 3 min
            0x00,  # temp_unit = C
            0x03,  # left_tc_hot
            0x02,  # left_tc_mid
            0x01,  # left_tc_cold
            0x00,  # left_tc_halt
            0xFB,  # left_current = -5C (0xFB as int8)
            0x64,  # battery_percent = 100
            0x0C,  # voltage_int = 12
            0x08,  # voltage_dec = 0.8 -> 12.8V
        ]
    )
    cmd = 0x01
    frame_len = len(data) + 3  # data + cmd + 2-byte checksum
    frame = bytearray([0xFE, 0xFE, frame_len, cmd])
    frame.extend(data)
    checksum = sum(frame) & 0xFFFF
    frame.extend(checksum.to_bytes(2, "big"))
    return bytes(frame)


@pytest.fixture
def valid_notify_payload_dual_zone() -> bytes:
    """Return a valid dual-zone notify payload."""
    data = bytes(
        [
            0x01,  # locked = True
            0x01,  # powered = True
            0x01,  # run_mode = Eco
            0x02,  # battery_saver = High
            0x05,  # left_target = 5C
            0x0A,  # temp_max = 10C
            0x00,  # temp_min = 0C
            0x02,  # left_ret_diff = 2
            0x03,  # start_delay = 3 min
            0x01,  # temp_unit = F
            0x03,  # left_tc_hot
            0x02,  # left_tc_mid
            0x01,  # left_tc_cold
            0x00,  # left_tc_halt
            0xFB,  # left_current = -5C
            0x64,  # battery_percent = 100
            0x0C,  # voltage_int = 12
            0x08,  # voltage_dec = 0.8
            # Right zone data (offset 0x12+)
            0xEC,  # right_target = -20C
            0x00,  # reserved
            0x00,  # reserved
            0x02,  # right_ret_diff
            0x03,  # right_tc_hot
            0x02,  # right_tc_mid
            0x01,  # right_tc_cold
            0x00,  # right_tc_halt
            0xE7,  # right_current = -25C
            0x01,  # running_status
        ]
    )
    cmd = 0x01
    frame_len = len(data) + 3
    frame = bytearray([0xFE, 0xFE, frame_len, cmd])
    frame.extend(data)
    checksum = sum(frame) & 0xFFFF
    frame.extend(checksum.to_bytes(2, "big"))
    return bytes(frame)


@pytest.fixture
def invalid_checksum_payload() -> bytes:
    """Return a payload with invalid checksum."""
    return bytes([0xFE, 0xFE, 0x06, 0x01, 0x00, 0x01, 0xFF, 0xFF])
