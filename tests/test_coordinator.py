"""Tests for the Bodega BLE coordinator."""

from __future__ import annotations

import pytest


class TestPacketCreation:
    """Tests for packet creation functions."""

    def test_create_packet_structure(self) -> None:
        """Test that _create_packet creates correct frame structure."""
        from custom_components.bodega_ble.coordinator import _create_packet

        data = bytes([0x01, 0x02, 0x03])
        result = _create_packet(data)

        # Frame structure: 0xFE 0xFE length data checksum(2 bytes)
        assert result[0] == 0xFE
        assert result[1] == 0xFE
        assert result[2] == len(data) + 2  # data + checksum
        assert result[3:6] == data

        # Verify checksum
        expected_checksum = sum(result[:-2]) & 0xFFFF
        actual_checksum = int.from_bytes(result[-2:], "big")
        assert actual_checksum == expected_checksum

    def test_create_packet_for_bind(self) -> None:
        """Test packet creation for bind command."""
        from custom_components.bodega_ble.const import CMD_BIND
        from custom_components.bodega_ble.coordinator import _create_packet

        result = _create_packet(bytes([CMD_BIND]))

        assert result[0:2] == bytes([0xFE, 0xFE])
        assert result[3] == CMD_BIND

    def test_create_packet_for_query(self) -> None:
        """Test packet creation for query command."""
        from custom_components.bodega_ble.const import CMD_QUERY
        from custom_components.bodega_ble.coordinator import _create_packet

        result = _create_packet(bytes([CMD_QUERY]))

        assert result[0:2] == bytes([0xFE, 0xFE])
        assert result[3] == CMD_QUERY


class TestInt8Conversion:
    """Tests for int8 conversion."""

    def test_int8_from_float_positive(self) -> None:
        """Test conversion of positive floats."""
        from custom_components.bodega_ble.coordinator import _int8_from_float

        assert _int8_from_float(5.0) == 5
        assert _int8_from_float(5.4) == 5
        assert _int8_from_float(5.6) == 6
        assert _int8_from_float(127.0) == 127

    def test_int8_from_float_negative(self) -> None:
        """Test conversion of negative floats."""
        from custom_components.bodega_ble.coordinator import _int8_from_float

        assert _int8_from_float(-5.0) == -5
        assert _int8_from_float(-20.0) == -20
        assert _int8_from_float(-128.0) == -128

    def test_int8_from_float_clamping(self) -> None:
        """Test that values are clamped to int8 range."""
        from custom_components.bodega_ble.coordinator import _int8_from_float

        assert _int8_from_float(200.0) == 127
        assert _int8_from_float(-200.0) == -128


class TestTemperatureConversion:
    """Tests for temperature unit conversions."""

    def test_to_celsius_from_celsius(self) -> None:
        """Test conversion when unit is already Celsius."""
        from custom_components.bodega_ble.coordinator import _to_celsius

        assert _to_celsius(10.0, "C") == 10.0
        assert _to_celsius(-20.0, "C") == -20.0

    def test_to_celsius_from_fahrenheit(self) -> None:
        """Test conversion from Fahrenheit to Celsius."""
        from custom_components.bodega_ble.coordinator import _to_celsius

        assert _to_celsius(32.0, "F") == pytest.approx(0.0, abs=0.01)
        assert _to_celsius(50.0, "F") == pytest.approx(10.0, abs=0.01)
        assert _to_celsius(-4.0, "F") == pytest.approx(-20.0, abs=0.01)

    def test_to_celsius_delta(self) -> None:
        """Test delta conversion (no offset)."""
        from custom_components.bodega_ble.coordinator import _to_celsius_delta

        assert _to_celsius_delta(5.0, "C") == 5.0
        assert _to_celsius_delta(9.0, "F") == pytest.approx(5.0, abs=0.01)


class TestRunModeParser:
    """Tests for run mode parsing."""

    def test_parse_run_mode_max(self) -> None:
        """Test parsing Max run mode."""
        from custom_components.bodega_ble.coordinator import _parse_run_mode

        assert _parse_run_mode("Max") == 0
        assert _parse_run_mode("max") == 0
        assert _parse_run_mode(0) == 0

    def test_parse_run_mode_eco(self) -> None:
        """Test parsing Eco run mode."""
        from custom_components.bodega_ble.coordinator import _parse_run_mode

        assert _parse_run_mode("Eco") == 1
        assert _parse_run_mode("eco") == 1
        assert _parse_run_mode(1) == 1


class TestBatterySaverParser:
    """Tests for battery saver level parsing."""

    def test_parse_battery_saver_low(self) -> None:
        """Test parsing Low battery saver level."""
        from custom_components.bodega_ble.coordinator import _parse_battery_saver

        assert _parse_battery_saver("Low") == 0
        assert _parse_battery_saver("low") == 0
        assert _parse_battery_saver(0) == 0

    def test_parse_battery_saver_mid(self) -> None:
        """Test parsing Mid battery saver level."""
        from custom_components.bodega_ble.coordinator import _parse_battery_saver

        assert _parse_battery_saver("Mid") == 1
        assert _parse_battery_saver("mid") == 1
        assert _parse_battery_saver("medium") == 1
        assert _parse_battery_saver(1) == 1

    def test_parse_battery_saver_high(self) -> None:
        """Test parsing High battery saver level."""
        from custom_components.bodega_ble.coordinator import _parse_battery_saver

        assert _parse_battery_saver("High") == 2
        assert _parse_battery_saver("high") == 2
        assert _parse_battery_saver(2) == 2
