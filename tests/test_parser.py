"""Tests for the Bodega BLE parser module."""

from __future__ import annotations

from custom_components.bodega_ble.const import (
    KEY_BATTERY_PERCENT,
    KEY_BATTERY_SAVER,
    KEY_BATTERY_VOLTAGE,
    KEY_LEFT_CURRENT,
    KEY_LEFT_TARGET,
    KEY_LOCKED,
    KEY_POWERED,
    KEY_RIGHT_CURRENT,
    KEY_RIGHT_TARGET,
    KEY_RUN_MODE,
    KEY_RUNNING_STATUS,
    KEY_TEMP_UNIT,
)
from custom_components.bodega_ble.parser import parse_notify_payload


class TestParseNotifyPayload:
    """Tests for parse_notify_payload function."""

    def test_valid_single_zone_payload(
        self, valid_notify_payload_single_zone: bytes
    ) -> None:
        """Test parsing a valid single-zone payload."""
        result = parse_notify_payload(valid_notify_payload_single_zone)

        assert result is not None
        assert result[KEY_LOCKED] is False
        assert result[KEY_POWERED] is True
        assert result[KEY_RUN_MODE] == "Max"
        assert result[KEY_BATTERY_SAVER] == "Mid"
        assert result[KEY_LEFT_TARGET] == 5
        assert result[KEY_TEMP_UNIT] == "C"
        assert result[KEY_LEFT_CURRENT] == -5
        assert result[KEY_BATTERY_PERCENT] == 100
        assert result[KEY_BATTERY_VOLTAGE] == 12.8

    def test_valid_dual_zone_payload(
        self, valid_notify_payload_dual_zone: bytes
    ) -> None:
        """Test parsing a valid dual-zone payload."""
        result = parse_notify_payload(valid_notify_payload_dual_zone)

        assert result is not None
        assert result[KEY_LOCKED] is True
        assert result[KEY_POWERED] is True
        assert result[KEY_RUN_MODE] == "Eco"
        assert result[KEY_BATTERY_SAVER] == "High"
        assert result[KEY_TEMP_UNIT] == "F"
        assert result[KEY_RIGHT_TARGET] == -20
        assert result[KEY_RIGHT_CURRENT] == -25
        assert result[KEY_RUNNING_STATUS] == 1

    def test_invalid_checksum(self, invalid_checksum_payload: bytes) -> None:
        """Test that invalid checksum returns empty dict."""
        result = parse_notify_payload(invalid_checksum_payload)
        assert result == {}

    def test_too_short_payload(self) -> None:
        """Test that payload shorter than 6 bytes returns empty dict."""
        result = parse_notify_payload(bytes([0xFE, 0xFE, 0x03]))
        assert result == {}

    def test_invalid_header(self) -> None:
        """Test that invalid header returns empty dict."""
        result = parse_notify_payload(bytes([0xFF, 0xFF, 0x06, 0x01, 0x00, 0x01]))
        assert result == {}

    def test_invalid_command(self) -> None:
        """Test that invalid command returns empty dict."""
        # Create a valid frame with command 0x03 (unsupported)
        data = bytes([0x00] * 18)
        cmd = 0x03
        frame_len = len(data) + 3
        frame = bytearray([0xFE, 0xFE, frame_len, cmd])
        frame.extend(data)
        checksum = sum(frame) & 0xFFFF
        frame.extend(checksum.to_bytes(2, "big"))

        result = parse_notify_payload(bytes(frame))
        assert result == {}

    def test_doubled_checksum_accepted(self) -> None:
        """Test that doubled checksum (firmware quirk) is accepted."""
        data = bytes(
            [
                0x00,  # locked
                0x01,  # powered
                0x00,  # run_mode
                0x01,  # battery_saver
                0x05,  # left_target
                0x0A,  # temp_max
                0x00,  # temp_min
                0x02,  # left_ret_diff
                0x03,  # start_delay
                0x00,  # temp_unit
                0x03,  # left_tc_hot
                0x02,  # left_tc_mid
                0x01,  # left_tc_cold
                0x00,  # left_tc_halt
                0xFB,  # left_current
                0x64,  # battery_percent
                0x0C,  # voltage_int
                0x08,  # voltage_dec
            ]
        )
        cmd = 0x01
        frame_len = len(data) + 3
        frame = bytearray([0xFE, 0xFE, frame_len, cmd])
        frame.extend(data)
        checksum = sum(frame) & 0xFFFF
        doubled = (checksum * 2) & 0xFFFF
        frame.extend(doubled.to_bytes(2, "big"))

        result = parse_notify_payload(bytes(frame))
        assert result != {}
        assert result[KEY_LOCKED] is False

    def test_battery_0x7f_not_reported(self) -> None:
        """Test that battery value 0x7F (invalid) is not reported."""
        data = bytes(
            [
                0x00,
                0x01,
                0x00,
                0x01,
                0x05,
                0x0A,
                0x00,
                0x02,
                0x03,
                0x00,
                0x03,
                0x02,
                0x01,
                0x00,
                0xFB,
                0x7F,  # battery_percent = 127 (invalid)
                0x0C,
                0x08,
            ]
        )
        cmd = 0x01
        frame_len = len(data) + 3
        frame = bytearray([0xFE, 0xFE, frame_len, cmd])
        frame.extend(data)
        checksum = sum(frame) & 0xFFFF
        frame.extend(checksum.to_bytes(2, "big"))

        result = parse_notify_payload(bytes(frame))
        assert KEY_BATTERY_PERCENT not in result
