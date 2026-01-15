# Bodega Bluetooth LE for Home Assistant

Home Assistant custom integration for Bodega/Alpicool/Brass Monkey BLE fridges.

## Features

- Config flow discovery by BLE name prefix and service UUID
- BLE GATT query/notify parsing with coordinator
- Sensors, binary sensors, and a bind button
- Bluetooth Proxy compatible (HA Bluetooth stack)

## Installation

### HACS (Custom Repository)

1. In HACS, go to **Integrations** → **Custom repositories**.
2. Add this repository URL and select **Integration**.
3. Install **Bodega BLE Fridge**.
4. Restart Home Assistant.
5. Add the integration via **Settings → Devices & Services**.

### Manual

Copy `custom_components/bodega_ble` into your Home Assistant config `custom_components` directory
and restart Home Assistant.

## Bluetooth Proxy Support

This integration uses Home Assistant's Bluetooth stack for discovery and GATT connections,
which is compatible with ESPHome Bluetooth Proxy when the proxy can establish active
connections to the device.

## Development

Run unit tests:

```sh
pip install -r requirements-dev.txt
pytest
```

## Notes

- Service UUID: `00001234-0000-1000-8000-00805f9b34fb`
- Write characteristic UUID: `00001235-0000-1000-8000-00805f9b34fb`
- Notify characteristic UUID: `00001236-0000-1000-8000-00805f9b34fb`

## License

MIT. See `LICENSE`.
