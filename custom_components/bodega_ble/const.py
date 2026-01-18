"""Constants for the Bodega BLE integration.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

DOMAIN = "bodega_ble"

NAME = "Bodega BLE Fridge"

# Update intervals
DEFAULT_SCAN_INTERVAL = 60  # seconds
MAX_BACKOFF_INTERVAL = 600  # seconds

# BLE timeouts
DEFAULT_CONNECT_TIMEOUT = 10
DEFAULT_COMMAND_TIMEOUT = 10

# Bodega BLE service and characteristics (UUIDs).
SERVICE_UUID = "00001234-0000-1000-8000-00805f9b34fb"
CHAR_WRITE_UUID = "00001235-0000-1000-8000-00805f9b34fb"
CHAR_NOTIFY_UUID = "00001236-0000-1000-8000-00805f9b34fb"

# BLE command codes
CMD_BIND = 0x00
CMD_QUERY = 0x01
CMD_SET = 0x02
CMD_SET_UNIT1_TARGET = 0x05
CMD_SET_UNIT2_TARGET = 0x06

# Command frames
# Checksum is sum of bytes [0:length-2] & 0xFFFF, big-endian
# FRAME_BIND: sum([0xFE, 0xFE, 0x03, 0x00]) = 0x1FF → checksum 0x01FF
FRAME_BIND = bytes([0xFE, 0xFE, 0x03, CMD_BIND, 0x01, 0xFF])
# FRAME_QUERY: sum([0xFE, 0xFE, 0x03, 0x01]) = 0x200 → checksum 0x0200
FRAME_QUERY = bytes([0xFE, 0xFE, 0x03, CMD_QUERY, 0x02, 0x00])

# Coordinator data keys
KEY_LOCKED = "locked"
KEY_POWERED = "powered"
KEY_LEFT_CURRENT = "left_current"
KEY_RIGHT_CURRENT = "right_current"
KEY_LEFT_TARGET = "left_target"
KEY_RIGHT_TARGET = "right_target"
KEY_TEMP_MAX = "temp_max"
KEY_TEMP_MIN = "temp_min"
KEY_LEFT_RET_DIFF = "left_ret_diff"
KEY_RIGHT_RET_DIFF = "right_ret_diff"
KEY_START_DELAY = "start_delay"
KEY_LEFT_TC_HOT = "left_tc_hot"
KEY_LEFT_TC_MID = "left_tc_mid"
KEY_LEFT_TC_COLD = "left_tc_cold"
KEY_LEFT_TC_HALT = "left_tc_halt"
KEY_RIGHT_TC_HOT = "right_tc_hot"
KEY_RIGHT_TC_MID = "right_tc_mid"
KEY_RIGHT_TC_COLD = "right_tc_cold"
KEY_RIGHT_TC_HALT = "right_tc_halt"
KEY_RUNNING_STATUS = "running_status"
KEY_RUN_MODE = "run_mode"
KEY_BATTERY_SAVER = "battery_saver"
KEY_TEMP_UNIT = "temp_unit"
KEY_BATTERY_PERCENT = "battery_percent"
KEY_BATTERY_VOLTAGE = "battery_voltage"
KEY_COMPRESSOR_STATUS = "compressor_status"
KEY_BLE_STATUS = "ble_status"

# BLE status values
BLE_STATUS_ADVERTISING = "Advertising"
BLE_STATUS_CONNECTED = "Connected"
BLE_STATUS_DISCONNECTED = "Disconnected"

# Device discovery
DEVICE_NAME_PREFIXES = ("WT-", "A1-", "AK1-", "AK2-", "AK3-")

# Service names
SERVICE_SET_LEFT_TARGET = "set_left_target"
SERVICE_SET_RIGHT_TARGET = "set_right_target"
SERVICE_SET_POWER = "set_power"
SERVICE_SET_LOCK = "set_lock"
SERVICE_SET_RUN_MODE = "set_run_mode"
SERVICE_SET_BATTERY_SAVER = "set_battery_saver"
