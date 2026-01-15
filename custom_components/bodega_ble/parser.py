"""Bodega BLE payload parsing helpers.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""
from __future__ import annotations

from typing import Any

from .const import (
    KEY_BATTERY_PERCENT,
    KEY_BATTERY_SAVER,
    KEY_BATTERY_VOLTAGE,
    KEY_COMPRESSOR_STATUS,
    KEY_LEFT_CURRENT,
    KEY_LEFT_RET_DIFF,
    KEY_LEFT_TARGET,
    KEY_LEFT_TC_COLD,
    KEY_LEFT_TC_HALT,
    KEY_LEFT_TC_HOT,
    KEY_LEFT_TC_MID,
    KEY_LOCKED,
    KEY_POWERED,
    KEY_RIGHT_CURRENT,
    KEY_RIGHT_RET_DIFF,
    KEY_RIGHT_TARGET,
    KEY_RIGHT_TC_COLD,
    KEY_RIGHT_TC_HALT,
    KEY_RIGHT_TC_HOT,
    KEY_RIGHT_TC_MID,
    KEY_RUN_MODE,
    KEY_RUNNING_STATUS,
    KEY_START_DELAY,
    KEY_TEMP_MAX,
    KEY_TEMP_MIN,
    KEY_TEMP_UNIT,
)


def parse_notify_payload(payload: bytes) -> dict[str, Any]:
    """Parse a Bodega notify frame into device-unit values."""
    if len(payload) < 6:
        return {}
    if payload[0] != 0xFE or payload[1] != 0xFE:
        return {}

    frame_len = payload[2]
    total_len = 3 + frame_len
    if frame_len < 3 or len(payload) != total_len:
        return {}

    expected = int.from_bytes(payload[total_len - 2 : total_len], "big")
    checksum = sum(payload[: total_len - 2]) & 0xFFFF
    if expected not in (checksum, (checksum * 2) & 0xFFFF):
        return {}

    cmd = payload[3]
    if cmd not in (0x01, 0x02):
        return {}

    data_len = frame_len - 3
    if data_len < 0x12:
        return {}

    data = payload[4 : total_len - 2]
    raw_unit = "F" if data[0x09] == 1 else "C"

    parsed: dict[str, Any] = {
        KEY_LOCKED: data[0x00] != 0,
        KEY_POWERED: data[0x01] != 0,
        KEY_RUN_MODE: _run_mode_to_text(data[0x02]),
        KEY_BATTERY_SAVER: _battery_saver_to_text(data[0x03]),
        KEY_TEMP_UNIT: raw_unit,
        KEY_START_DELAY: data[0x08],
        KEY_LEFT_TARGET: _int8(data[0x04]),
        KEY_LEFT_CURRENT: _int8(data[0x0E]),
        KEY_TEMP_MAX: _int8(data[0x05]),
        KEY_TEMP_MIN: _int8(data[0x06]),
        KEY_LEFT_RET_DIFF: _int8(data[0x07]),
        KEY_LEFT_TC_HOT: _int8(data[0x0A]),
        KEY_LEFT_TC_MID: _int8(data[0x0B]),
        KEY_LEFT_TC_COLD: _int8(data[0x0C]),
        KEY_LEFT_TC_HALT: _int8(data[0x0D]),
    }

    battery = data[0x0F]
    if battery != 0x7F:
        parsed[KEY_BATTERY_PERCENT] = battery

    voltage_int = data[0x10]
    voltage_dec = data[0x11]
    voltage = float(voltage_int) + (voltage_dec / 10.0)
    parsed[KEY_BATTERY_VOLTAGE] = voltage
    parsed[KEY_COMPRESSOR_STATUS] = _compressor_status(voltage)

    if data_len >= 0x1C:
        parsed[KEY_RIGHT_TARGET] = _int8(data[0x12])
        parsed[KEY_RIGHT_RET_DIFF] = _int8(data[0x15])
        parsed[KEY_RIGHT_TC_HOT] = _int8(data[0x16])
        parsed[KEY_RIGHT_TC_MID] = _int8(data[0x17])
        parsed[KEY_RIGHT_TC_COLD] = _int8(data[0x18])
        parsed[KEY_RIGHT_TC_HALT] = _int8(data[0x19])
        parsed[KEY_RIGHT_CURRENT] = _int8(data[0x1A])
        parsed[KEY_RUNNING_STATUS] = data[0x1B]

    return parsed


def _int8(value: int) -> int:
    """Convert unsigned byte to signed int8."""
    return int.from_bytes(bytes([value]), "big", signed=True)


def _run_mode_to_text(mode: int) -> str:
    if mode == 0:
        return "Max"
    if mode == 1:
        return "Eco"
    return "Unknown"


def _battery_saver_to_text(level: int) -> str:
    if level == 0:
        return "Low"
    if level == 1:
        return "Mid"
    if level == 2:
        return "High"
    return "Unknown"


def _compressor_status(voltage: float) -> str:
    if voltage >= 24.0:
        return "Compressor Off"
    if 23.0 < voltage < 23.9:
        return "Compressor On"
    return "Unknown"
