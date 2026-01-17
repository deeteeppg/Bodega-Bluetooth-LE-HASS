# Bodega BLE Fridge for Home Assistant

[![CI](https://github.com/deeteeppg/Bodega-Bluetooth-LE-HASS/actions/workflows/ci.yml/badge.svg)](https://github.com/deeteeppg/Bodega-Bluetooth-LE-HASS/actions/workflows/ci.yml)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-blue.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Home Assistant custom integration for **Bodega** and **Alpicool** portable fridges via Bluetooth Low Energy (BLE).

## Supported Devices

| Model Prefix | Type | Zones | Status |
|--------------|------|-------|--------|
| WT-* | Bodega | Single | Tested |
| A1-* | Alpicool | Single | Community Reported |
| AK1-* | Alpicool | Dual | Community Reported |
| AK2-* | Alpicool | Dual | Community Reported |
| AK3-* | Alpicool | Dual | Community Reported |

> **Note:** These fridges are sold under various brand names including Bodega, Alpicool, and others. If your fridge's Bluetooth name starts with one of the prefixes above, it should work with this integration.

## Features

- **Automatic Discovery**: Devices are discovered automatically via Bluetooth
- **Temperature Monitoring**: Current and target temperatures for fridge/freezer zones
- **Battery Status**: Battery percentage and voltage monitoring
- **Compressor Status**: Know when the compressor is running
- **Control Services**: Set target temperatures, power, lock, run mode, and battery saver
- **Bluetooth Proxy Support**: Works with ESPHome Bluetooth Proxies
- **Configurable Update Interval**: Adjust polling frequency via options

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to **Integrations** → **Custom repositories**
3. Add this repository URL: `https://github.com/deeteeppg/Bodega-Bluetooth-LE-HASS`
4. Select **Integration** as the category
5. Click **Add**
6. Search for "Bodega BLE Fridge" and install it
7. Restart Home Assistant
8. Go to **Settings** → **Devices & Services** → **Add Integration** → **Bodega BLE Fridge**

### Manual Installation

1. Download the latest release from the [Releases](https://github.com/deeteeppg/Bodega-Bluetooth-LE-HASS/releases) page
2. Extract and copy the `custom_components/bodega_ble` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Add Integration** → **Bodega BLE Fridge**

## Configuration

### Adding a Device

1. Ensure your fridge is powered on and within Bluetooth range
2. Go to **Settings** → **Devices & Services**
3. Click **Add Integration** and search for "Bodega BLE Fridge"
4. If your fridge is discovered automatically, confirm the device
5. If not discovered, enter the Bluetooth MAC address manually

### Options

After adding the integration, you can configure:

| Option | Description | Default |
|--------|-------------|---------|
| Update Interval | How often to poll the fridge (seconds) | 60 |

To change options: **Settings** → **Devices & Services** → **Bodega BLE Fridge** → **Configure**

## Entities

### Sensors

| Entity | Description |
|--------|-------------|
| Fridge Temperature | Current temperature of the fridge zone |
| Freezer Temperature | Current temperature of the freezer zone (dual-zone models) |
| Fridge Target | Target temperature for the fridge zone |
| Freezer Target | Target temperature for the freezer zone (dual-zone models) |
| Battery | Battery percentage (if supported) |
| Battery Voltage | Battery voltage reading |
| Compressor | Compressor status (On/Off/Unknown) |
| BLE Status | Bluetooth connection status |
| Run Mode | Current run mode (Max/Eco) |
| Battery Saver | Battery saver level (Low/Mid/High) |

### Binary Sensors

| Entity | Description |
|--------|-------------|
| Powered | Whether the fridge is powered on |
| Locked | Whether the controls are locked |

### Buttons

| Entity | Description |
|--------|-------------|
| Bind | Send bind command to pair with the fridge |

## Services

The integration provides the following services:

### `bodega_ble.set_left_target`
Set the fridge (left zone) target temperature.

### `bodega_ble.set_right_target`
Set the freezer (right zone) target temperature.

### `bodega_ble.set_power`
Power the fridge on or off.

### `bodega_ble.set_lock`
Lock or unlock the fridge controls.

### `bodega_ble.set_run_mode`
Set the run mode (Max or Eco).

### `bodega_ble.set_battery_saver`
Set the battery saver level (Low, Mid, or High).

> **Note:** All services require the `entry_id` parameter. You can find this in the device info or via Developer Tools.

## Bluetooth Proxy Support

This integration fully supports Home Assistant's Bluetooth stack, including [ESPHome Bluetooth Proxies](https://esphome.io/components/bluetooth_proxy.html). This allows you to:

- Extend Bluetooth range using ESP32 devices
- Place the fridge further from your Home Assistant server
- Use multiple proxies for better coverage

For best results with a Bluetooth Proxy:
- Use an ESP32 with `active: true` in the `bluetooth_proxy` configuration
- Place the proxy within ~10 meters of the fridge
- Ensure the proxy has good WiFi connectivity

## Troubleshooting

### Device Not Found

1. **Check Bluetooth is enabled** on your Home Assistant host
2. **Verify the fridge is powered on** and the display is active
3. **Move closer** - BLE range is typically 10 meters or less
4. **Check for interference** from other 2.4GHz devices (WiFi, microwaves)
5. **Try a Bluetooth Proxy** if your HA server is far from the fridge

### Connection Drops / Unavailable

1. **Check distance** - the fridge may be too far from the Bluetooth adapter
2. **Check for interference** - move away from WiFi routers and other BLE devices
3. **Increase update interval** - try 120 or 180 seconds in options
4. **Check the BLE Status sensor** - it shows connection state

### Wrong Temperature Units

The integration automatically converts temperatures to match your Home Assistant unit system (configured in **Settings** → **System** → **General**).

### Debug Logging

To enable debug logging, add to your `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.bodega_ble: debug
    bleak: debug
```

After restarting, check the logs in **Settings** → **System** → **Logs**.

### Diagnostics

You can download diagnostics for troubleshooting:
1. Go to **Settings** → **Devices & Services**
2. Click on your Bodega BLE Fridge device
3. Click the three-dot menu → **Download diagnostics**

This file contains (with sensitive data redacted):
- Configuration settings
- Current coordinator data
- BLE connection status

## Technical Details

### BLE Protocol

| Item | Value |
|------|-------|
| Service UUID | `00001234-0000-1000-8000-00805f9b34fb` |
| Write Characteristic | `00001235-0000-1000-8000-00805f9b34fb` |
| Notify Characteristic | `00001236-0000-1000-8000-00805f9b34fb` |

### Dependencies

- [bleak](https://github.com/hbldh/bleak) >= 0.21.0
- [bleak-retry-connector](https://github.com/Bluetooth-Devices/bleak-retry-connector) >= 3.4.0

## Known Limitations

- **Single connection**: Only one device can connect to the fridge at a time. If the mobile app is connected, Home Assistant cannot connect.
- **Range**: BLE range is limited. Consider using a Bluetooth Proxy for better coverage.
- **Battery sensor**: Some models don't report battery percentage accurately.
- **Compressor status**: Inferred from voltage readings; may show "Unknown" on some models.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Run linting: `ruff check . && ruff format .`
4. Run tests: `pytest`
5. Submit a pull request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/deeteeppg/Bodega-Bluetooth-LE-HASS.git
cd Bodega-Bluetooth-LE-HASS

# Install development dependencies
pip install -r requirements-dev.txt
pip install ruff

# Run linting
ruff check .
ruff format --check .

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Home Assistant community for BLE integration patterns
- Thanks to contributors who have tested with various fridge models
