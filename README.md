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

## Icons

Project icons live in `assets/icons/` (SVG/PNG source files for docs and releases):

- `bodega_ble_main.svg` (primary integration icon)
- `bodega_ble_badge.svg` (badge)
- `bodega_ble_device.svg` (device icon)
- PNG renders at 64px and 256px

HACS shows the repo icon from the repository root `icon.png`/`logo.png`.
Home Assistant shows the integration logo/icon from the official brands repo
(custom integrations must submit `custom_integrations/<domain>/icon.png` and
`logo.png` to `home-assistant/brands`). Custom assets inside
`custom_components/` will not render in the HA Integrations UI until the brands
submission is merged.

See `brands/README.md` for a ready-to-submit brands patch and PR steps.

If icons do not appear in HACS immediately, re-download the integration in HACS,
restart Home Assistant, and hard-refresh your browser cache.

## Notes

- Service UUID: `00001234-0000-1000-8000-00805f9b34fb`
- Write characteristic UUID: `00001235-0000-1000-8000-00805f9b34fb`
- Notify characteristic UUID: `00001236-0000-1000-8000-00805f9b34fb`

## License

MIT. See `LICENSE`.

## RELEASE_NOTES

- Changed: Bluetooth discovery now matches the service UUID in addition to name prefixes.
- Changed: Startup retries refresh if the BLE device is not immediately visible after reboot.
- Docs: Clarified HACS vs Home Assistant icon sources and added brands submission helper.
- Upgrade: In HACS, re-download the integration and confirm `/config/custom_components/bodega_ble/manifest.json` exists.
- Cache: Clear HACS repo cache, restart Home Assistant, and hard-refresh the browser for icon updates.
- Troubleshooting: Check HA logs for `bodega_ble`, confirm Bluetooth is enabled and the fridge advertises, and re-add the device if its BLE address changed.
