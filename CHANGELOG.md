# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Options flow for configuring update interval (60-600 seconds)
- Diagnostics support for troubleshooting
- Translations file (`translations/en.json`) for localization
- Binary sensor device classes (Lock, Power)
- Comprehensive README with troubleshooting guide
- CI workflow with ruff linting and hassfest validation
- `pyproject.toml` with ruff configuration

### Changed
- Improved DeviceInfo with proper manufacturer (Bodega / Alpicool) and model detection
- Replaced deprecated `async_timeout` with `asyncio.timeout` (Python 3.11+)
- Fixed type annotations (`callable` → `Callable`)

### Fixed
- Corrected FRAME_QUERY checksum documentation

## [0.2.0] - 2024-XX-XX

### Added
- Initial release with HACS support
- Config flow with Bluetooth discovery
- Support for WT-*, A1-*, AK1-*, AK2-*, AK3-* device prefixes
- Sensors for temperature, battery, compressor status
- Binary sensors for power and lock state
- Bind button for device pairing
- Services for controlling fridge settings
- Backoff mechanism for connection retries

## [0.1.0] - 2024-XX-XX

### Added
- Initial development version
