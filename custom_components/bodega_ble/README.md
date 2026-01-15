# Bodega BLE Fridge

Home Assistant custom integration for Bodega fridges using BLE.

## Features

- BLE scan + selection in config flow
- Query frame every 60 seconds
- Sensors, binary sensors, and a bind button
- Writable controls for targets, power, lock, run mode, and battery saver
- Set commands follow BrassMonkeyFridgeMonitor framing + checksums

## Notes

- Known BLE name prefixes: `WT-`, `A1-`, `AK1-`, `AK2-`, `AK3-`.
- Discovery also matches the Bodega BLE service UUID for devices that omit names.
- Connecting a BLE client can temporarily hide advertisements until disconnect.
- Service UUID: `00001234-0000-1000-8000-00805f9b34fb`
- Write characteristic UUID: `00001235-0000-1000-8000-00805f9b34fb`
- Notify characteristic UUID: `00001236-0000-1000-8000-00805f9b34fb`

## Bluetooth Proxy Support

This integration uses Home Assistant's Bluetooth stack for discovery and GATT
connections, which is compatible with ESPHome Bluetooth Proxy when the proxy
can establish active connections to the device.

Troubleshooting tips:
- Ensure the proxy is close enough to maintain a reliable connection.
- If the device requires pairing/bonding, proxy support may be limited.
- Check Home Assistant logs for "Device not found" or "Timeout" errors.

## Development

Install test dependencies and run the unit tests:

```sh
pip install -r requirements-dev.txt
pytest
```

CI runs `pytest` via GitHub Actions in `.github/workflows/ci.yml`.
