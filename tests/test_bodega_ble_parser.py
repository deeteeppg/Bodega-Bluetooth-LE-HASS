"""Tests for Bodega BLE parsing."""
from __future__ import annotations

from custom_components.bodega_ble.const import (
    KEY_BATTERY_PERCENT,
    KEY_BATTERY_VOLTAGE,
    KEY_LEFT_CURRENT,
    KEY_LEFT_TARGET,
    KEY_POWERED,
    KEY_RIGHT_CURRENT,
    KEY_RIGHT_TARGET,
    KEY_TEMP_UNIT,
)
from custom_components.bodega_ble.parser import parse_notify_payload


def _build_frame(cmd: int, data: bytes) -> bytes:
    frame_len = 1 + len(data) + 2
    frame = bytearray([0xFE, 0xFE, frame_len, cmd])
    frame.extend(data)
    checksum = sum(frame) & 0xFFFF
    frame.extend(checksum.to_bytes(2, "big"))
    return bytes(frame)


def test_parse_notify_payload_single_zone() -> None:
    data = bytearray([0x00] * 0x12)
    data[0x01] = 1
    data[0x04] = 5
    data[0x05] = 10
    data[0x06] = 2
    data[0x07] = 1
    data[0x08] = 3
    data[0x09] = 0
    data[0x0E] = 6
    data[0x0F] = 80
    data[0x10] = 12
    data[0x11] = 3

    payload = _build_frame(0x01, data)
    parsed = parse_notify_payload(payload)

    assert parsed[KEY_POWERED] is True
    assert parsed[KEY_TEMP_UNIT] == "C"
    assert parsed[KEY_LEFT_TARGET] == 5
    assert parsed[KEY_LEFT_CURRENT] == 6
    assert parsed[KEY_BATTERY_PERCENT] == 80
    assert parsed[KEY_BATTERY_VOLTAGE] == 12.3


def test_parse_notify_payload_dual_zone() -> None:
    data = bytearray([0x00] * 0x1C)
    data[0x01] = 1
    data[0x04] = 4
    data[0x09] = 1
    data[0x0E] = 7
    data[0x12] = 2
    data[0x1A] = 8

    payload = _build_frame(0x02, data)
    parsed = parse_notify_payload(payload)

    assert parsed[KEY_TEMP_UNIT] == "F"
    assert parsed[KEY_LEFT_TARGET] == 4
    assert parsed[KEY_RIGHT_TARGET] == 2
    assert parsed[KEY_LEFT_CURRENT] == 7
    assert parsed[KEY_RIGHT_CURRENT] == 8


def test_parse_notify_payload_invalid_checksum() -> None:
    data = bytearray([0x00] * 0x12)
    payload = bytearray(_build_frame(0x01, data))
    payload[-1] = (payload[-1] + 1) & 0xFF
    assert parse_notify_payload(bytes(payload)) == {}
