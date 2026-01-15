"""DataUpdateCoordinator for Bodega BLE fridges.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

import async_timeout
from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice
from bleak_retry_connector import BleakError as BleakRetryError, establish_connection

from homeassistant.components.bluetooth import (
    BluetoothCallbackMatcher,
    BluetoothChange,
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
    async_ble_device_from_address,
    async_register_callback,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import (
    BLE_STATUS_ADVERTISING,
    BLE_STATUS_CONNECTED,
    BLE_STATUS_DISCONNECTED,
    CHAR_NOTIFY_UUID,
    CHAR_WRITE_UUID,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_COMMAND_TIMEOUT,
    DEFAULT_CONNECT_TIMEOUT,
    DOMAIN,
    FRAME_BIND,
    FRAME_QUERY,
    KEY_BATTERY_SAVER,
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
    KEY_START_DELAY,
    KEY_TEMP_MAX,
    KEY_TEMP_MIN,
    KEY_TEMP_UNIT,
    KEY_BLE_STATUS,
    MAX_BACKOFF_INTERVAL,
)
from .parser import parse_notify_payload

if TYPE_CHECKING:
    from . import BodegaBleConfigEntry

_LOGGER = logging.getLogger(__name__)


class BodegaBleCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for Bodega BLE device data."""

    config_entry: BodegaBleConfigEntry

    def __init__(self, hass, entry: BodegaBleConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.address = entry.data["address"]
        self._connect_lock = asyncio.Lock()
        self._cancel_bluetooth_callback: callable | None = None
        self._ble_device: BLEDevice | None = None
        self._last_seen: dt_util.dt.datetime | None = None
        self._base_interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL)
        self._backoff_step = 0

    def async_start(self) -> callable:
        """Start listening for Bluetooth advertisements."""
        @callback
        def _async_bluetooth_callback(
            service_info: BluetoothServiceInfoBleak,
            change: BluetoothChange,
        ) -> None:
            if change == BluetoothChange.ADVERTISEMENT:
                self._ble_device = service_info.device
                self._last_seen = dt_util.utcnow()
                self.async_set_updated_data(
                    {
                        **(self.data or {}),
                        KEY_BLE_STATUS: BLE_STATUS_ADVERTISING,
                    }
                )

        self._cancel_bluetooth_callback = async_register_callback(
            self.hass,
            _async_bluetooth_callback,
            BluetoothCallbackMatcher(address=self.address),
            BluetoothScanningMode.PASSIVE,
        )

        return self._cancel_bluetooth_callback

    async def async_send_bind(self) -> None:
        """Send bind command to the fridge."""
        await self._async_send_command(FRAME_BIND)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Bluetooth device."""
        try:
            async with self._connect_lock:
                data = await self._async_query_state()
                self._reset_backoff()
                return data
        except EOFError as err:
            _LOGGER.debug(
                "BLE disconnect glitch while updating data: %s", err
            )
            self._set_ble_status(BLE_STATUS_DISCONNECTED)
            self._increase_backoff()
            return self.data or {}
        except (BleakError, BleakRetryError) as err:
            self._set_ble_status(BLE_STATUS_DISCONNECTED)
            self._increase_backoff()
            raise UpdateFailed(f"BLE error: {err}") from err
        except asyncio.TimeoutError as err:
            self._set_ble_status(BLE_STATUS_DISCONNECTED)
            self._increase_backoff()
            raise UpdateFailed("Timeout waiting for BLE response") from err

    async def _async_send_command(self, payload: bytes) -> None:
        """Connect and send a write-only command."""
        async with self._connect_lock:
            ble_device = self._async_get_ble_device()
            if not ble_device:
                self._set_ble_status(BLE_STATUS_DISCONNECTED)
                raise UpdateFailed("Device not found")

            self._set_ble_status(BLE_STATUS_CONNECTED)
            async with async_timeout.timeout(DEFAULT_CONNECT_TIMEOUT):
                async with await establish_connection(
                    BleakClient, ble_device, self.address
                ) as client:
                    async with async_timeout.timeout(DEFAULT_COMMAND_TIMEOUT):
                        await client.write_gatt_char(
                            _format_uuid(CHAR_WRITE_UUID), payload, response=True
                        )

    async def _async_query_state(self) -> dict[str, Any]:
        """Send a query and parse the notify response."""
        ble_device = self._async_get_ble_device()
        if not ble_device:
            self._set_ble_status(BLE_STATUS_DISCONNECTED)
            raise UpdateFailed("Device not found")

        notify_future: asyncio.Future[bytes] = self.hass.loop.create_future()

        def _handle_notify(_: int, payload: bytearray) -> None:
            if not notify_future.done():
                notify_future.set_result(bytes(payload))

        async with async_timeout.timeout(DEFAULT_CONNECT_TIMEOUT):
            async with await establish_connection(
                BleakClient, ble_device, self.address
            ) as client:
                await client.start_notify(
                    _format_uuid(CHAR_NOTIFY_UUID), _handle_notify
                )
                async with async_timeout.timeout(DEFAULT_COMMAND_TIMEOUT):
                    await client.write_gatt_char(
                        _format_uuid(CHAR_WRITE_UUID), FRAME_QUERY, response=True
                    )
                try:
                    payload = await asyncio.wait_for(
                        notify_future, timeout=DEFAULT_COMMAND_TIMEOUT
                    )
                finally:
                    await client.stop_notify(_format_uuid(CHAR_NOTIFY_UUID))

        raw_data = parse_notify_payload(payload)
        if not raw_data:
            raise UpdateFailed("No valid payload received")

        data = self._normalize_data(raw_data)
        data[KEY_BLE_STATUS] = BLE_STATUS_CONNECTED
        return data

    def _normalize_data(self, raw: dict[str, Any]) -> dict[str, Any]:
        unit = raw.get(KEY_TEMP_UNIT, "C")
        parsed = dict(raw)
        temp_keys = (
            KEY_LEFT_TARGET,
            KEY_RIGHT_TARGET,
            KEY_LEFT_CURRENT,
            KEY_RIGHT_CURRENT,
            KEY_TEMP_MAX,
            KEY_TEMP_MIN,
        )
        delta_keys = (
            KEY_LEFT_RET_DIFF,
            KEY_RIGHT_RET_DIFF,
            KEY_LEFT_TC_HOT,
            KEY_LEFT_TC_MID,
            KEY_LEFT_TC_COLD,
            KEY_LEFT_TC_HALT,
            KEY_RIGHT_TC_HOT,
            KEY_RIGHT_TC_MID,
            KEY_RIGHT_TC_COLD,
            KEY_RIGHT_TC_HALT,
        )
        for key in temp_keys:
            if key in parsed:
                parsed[key] = self._normalize_temp(parsed[key], unit)
        for key in delta_keys:
            if key in parsed:
                parsed[key] = self._normalize_delta(parsed[key], unit)
        return parsed

    def _async_get_ble_device(self) -> BLEDevice | None:
        ble_device = async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if ble_device:
            self._ble_device = ble_device
        return ble_device or self._ble_device

    def _set_ble_status(self, status: str) -> None:
        self.async_set_updated_data({**(self.data or {}), KEY_BLE_STATUS: status})

    def _increase_backoff(self) -> None:
        self._backoff_step = min(self._backoff_step + 1, 5)
        next_seconds = min(
            DEFAULT_SCAN_INTERVAL * (2**self._backoff_step), MAX_BACKOFF_INTERVAL
        )
        self.update_interval = timedelta(seconds=next_seconds)
        _LOGGER.debug("BLE backoff set to %s seconds", next_seconds)

    def _reset_backoff(self) -> None:
        if self._backoff_step:
            self._backoff_step = 0
            self.update_interval = self._base_interval

    def _normalize_temp(self, raw: int, unit: str) -> float:
        """Normalize a temperature reading to HA's unit system."""
        value_c = _to_celsius(raw, unit)
        return _to_hass_temp(value_c, self.hass.config.units.temperature_unit)

    def _normalize_delta(self, raw: int, unit: str) -> float:
        """Normalize a delta reading to HA's unit system."""
        value_c = _to_celsius_delta(raw, unit)
        target_unit = self.hass.config.units.temperature_unit
        if target_unit == UnitOfTemperature.FAHRENHEIT:
            return (value_c * 9.0 / 5.0)
        return value_c

    async def async_set_left_target(self, temperature: float) -> None:
        """Set the left target temperature."""
        payload = self._encode_target_command(0x05, temperature)
        await self._async_send_command(payload)

    async def async_set_right_target(self, temperature: float) -> None:
        """Set the right target temperature."""
        payload = self._encode_target_command(0x06, temperature)
        await self._async_send_command(payload)

    async def async_set_power(self, powered: bool) -> None:
        """Set fridge power state."""
        await self._async_send_command(
            self._encode_set_other({"powered": powered})
        )

    async def async_set_lock(self, locked: bool) -> None:
        """Set fridge lock state."""
        await self._async_send_command(
            self._encode_set_other({"locked": locked})
        )

    async def async_set_run_mode(self, mode: str) -> None:
        """Set fridge run mode (Max/Eco)."""
        await self._async_send_command(
            self._encode_set_other({"run_mode": _parse_run_mode(mode)})
        )

    async def async_set_battery_saver(self, level: str) -> None:
        """Set battery saver level (Low/Mid/High)."""
        await self._async_send_command(
            self._encode_set_other({"battery_saver": _parse_battery_saver(level)})
        )

    def _encode_target_command(self, command: int, temperature: float) -> bytes:
        """Encode a target temperature command."""
        data = self._require_last_data()
        unit = _unit_from_data(data)
        temp = _to_device_temp(temperature, unit, self.hass)
        return _create_packet(bytes([command, _int8_from_float(temp)]))

    def _encode_set_other(self, updates: dict[str, Any]) -> bytes:
        """Encode a Set command using the last query data plus updates."""
        data = self._require_last_data()
        unit = _unit_from_data(data)

        locked = updates.get(KEY_LOCKED, data.get(KEY_LOCKED, False))
        powered = updates.get(KEY_POWERED, data.get(KEY_POWERED, False))
        run_mode = updates.get("run_mode", _run_mode_from_data(data))
        battery_saver = updates.get(
            "battery_saver", _battery_saver_from_data(data)
        )

        left_target = _to_device_temp(
            data[KEY_LEFT_TARGET], unit, self.hass
        )
        temp_max = _to_device_temp(data[KEY_TEMP_MAX], unit, self.hass)
        temp_min = _to_device_temp(data[KEY_TEMP_MIN], unit, self.hass)
        left_ret_diff = _to_device_delta(
            data[KEY_LEFT_RET_DIFF], unit, self.hass
        )
        start_delay = int(data[KEY_START_DELAY])
        left_tc_hot = _to_device_delta(
            data[KEY_LEFT_TC_HOT], unit, self.hass
        )
        left_tc_mid = _to_device_delta(
            data[KEY_LEFT_TC_MID], unit, self.hass
        )
        left_tc_cold = _to_device_delta(
            data[KEY_LEFT_TC_COLD], unit, self.hass
        )
        left_tc_halt = _to_device_delta(
            data[KEY_LEFT_TC_HALT], unit, self.hass
        )

        payload = [
            0x02,
            int(locked),
            int(powered),
            int(run_mode),
            int(battery_saver),
            _int8_from_float(left_target),
            _int8_from_float(temp_max),
            _int8_from_float(temp_min),
            _int8_from_float(left_ret_diff),
            start_delay & 0xFF,
            1 if unit == "F" else 0,
            _int8_from_float(left_tc_hot),
            _int8_from_float(left_tc_mid),
            _int8_from_float(left_tc_cold),
            _int8_from_float(left_tc_halt),
        ]

        if KEY_RIGHT_TARGET in data:
            right_target = _to_device_temp(
                data[KEY_RIGHT_TARGET], unit, self.hass
            )
            right_ret_diff = _to_device_delta(
                data[KEY_RIGHT_RET_DIFF], unit, self.hass
            )
            right_tc_hot = _to_device_delta(
                data[KEY_RIGHT_TC_HOT], unit, self.hass
            )
            right_tc_mid = _to_device_delta(
                data[KEY_RIGHT_TC_MID], unit, self.hass
            )
            right_tc_cold = _to_device_delta(
                data[KEY_RIGHT_TC_COLD], unit, self.hass
            )
            right_tc_halt = _to_device_delta(
                data[KEY_RIGHT_TC_HALT], unit, self.hass
            )

            payload.extend(
                [
                    _int8_from_float(right_target),
                    0x00,
                    0x00,
                    _int8_from_float(right_ret_diff),
                    _int8_from_float(right_tc_hot),
                    _int8_from_float(right_tc_mid),
                    _int8_from_float(right_tc_cold),
                    _int8_from_float(right_tc_halt),
                    0x00,
                    0x00,
                    0x00,
                ]
            )

        return _create_packet(bytes(payload))

    def _require_last_data(self) -> dict[str, Any]:
        if not self.data:
            raise HomeAssistantError("No recent fridge data to build command")
        return self.data


def _format_uuid(value: str) -> str:
    """Expand 16-bit UUIDs into the full BLE UUID string."""
    if len(value) == 4:
        return f"0000{value}-0000-1000-8000-00805f9b34fb"
    return value


def _int8_from_float(value: float) -> int:
    rounded = int(round(value))
    return max(-128, min(127, rounded))


def _to_celsius(value: float, unit: str) -> float:
    if unit == "F":
        return (value - 32.0) * 5.0 / 9.0
    return value


def _to_celsius_delta(value: float, unit: str) -> float:
    if unit == "F":
        return value * 5.0 / 9.0
    return value


def _to_hass_temp(value_c: float, target_unit: UnitOfTemperature) -> float:
    if target_unit == UnitOfTemperature.FAHRENHEIT:
        return (value_c * 9.0 / 5.0) + 32.0
    return value_c


def _to_device_temp(
    value: float, device_unit: str, hass
) -> float:
    hass_unit = hass.config.units.temperature_unit
    value_c = value
    if hass_unit == UnitOfTemperature.FAHRENHEIT:
        value_c = (value - 32.0) * 5.0 / 9.0
    if device_unit == "F":
        return (value_c * 9.0 / 5.0) + 32.0
    return value_c


def _to_device_delta(
    value: float, device_unit: str, hass
) -> float:
    hass_unit = hass.config.units.temperature_unit
    value_c = value
    if hass_unit == UnitOfTemperature.FAHRENHEIT:
        value_c = value * 5.0 / 9.0
    if device_unit == "F":
        return value_c * 9.0 / 5.0
    return value_c


def _create_packet(data: bytes) -> bytes:
    frame = bytearray()
    frame.extend([0xFE, 0xFE, (len(data) + 2) & 0xFF])
    frame.extend(data)
    checksum = sum(frame) & 0xFFFF
    frame.extend(checksum.to_bytes(2, "big"))
    return bytes(frame)


def _unit_from_data(data: dict[str, Any]) -> str:
    unit = data.get(KEY_TEMP_UNIT, "C")
    return "F" if unit == "F" else "C"


def _run_mode_from_data(data: dict[str, Any]) -> int:
    return _parse_run_mode(data.get(KEY_RUN_MODE, "Max"))


def _battery_saver_from_data(data: dict[str, Any]) -> int:
    return _parse_battery_saver(data.get(KEY_BATTERY_SAVER, "Low"))


def _parse_run_mode(mode: str | int) -> int:
    if isinstance(mode, int):
        return 1 if mode == 1 else 0
    value = str(mode).strip().lower()
    if value in ("eco", "1"):
        return 1
    return 0


def _parse_battery_saver(level: str | int) -> int:
    if isinstance(level, int):
        if level in (0, 1, 2):
            return level
        return 0
    value = str(level).strip().lower()
    if value in ("mid", "medium", "1"):
        return 1
    if value in ("high", "2"):
        return 2
    return 0
