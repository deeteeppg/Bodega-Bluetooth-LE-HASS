# Home Assistant Integration Review Playbook

Lessons learned from production-readiness review sessions.

## Pre-Review Checklist

Before making any changes:

```bash
# 1. Check existing CI status
gh run list --branch main --limit 5

# 2. Check Python version matrix in CI
cat .github/workflows/*.yml | grep python-version

# 3. Verify pytest-homeassistant-custom-component version
cat requirements-dev.txt | grep homeassistant
```

## Common Compatibility Issues

### Python 3.11 Type Alias Pattern

Generic type subscripts like `ConfigEntry[T]` are not valid at runtime in Python 3.11.

```python
# BAD - Fails at runtime in Python 3.11
from typing import TypeAlias
MyConfigEntry: TypeAlias = ConfigEntry[MyCoordinator]

# GOOD - Works in all Python versions
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeAlias
    MyConfigEntry: TypeAlias = ConfigEntry[MyCoordinator]
else:
    MyConfigEntry = ConfigEntry
```

### HA Version-Safe Imports

```python
# BAD - ConfigFlowResult only available in HA 2024.1+
from homeassistant.config_entries import ConfigFlowResult

# GOOD - FlowResult works in all HA versions
from homeassistant.data_entry_flow import FlowResult
```

### Deprecated async_timeout

```python
# BAD - async_timeout deprecated in Python 3.11+
import async_timeout
async with async_timeout.timeout(10):
    ...

# GOOD - Use asyncio.timeout directly
import asyncio
async with asyncio.timeout(10):
    ...
```

### Type Hints

```python
# BAD - callable is Python builtin, not a type
self._callback: callable | None = None

# GOOD - Use Callable from collections.abc
from collections.abc import Callable
self._callback: Callable[[], None] | None = None
```

## Manifest Requirements (hassfest)

Keys must be ordered: `domain`, `name`, then **alphabetical**.

```json
{
  "domain": "my_integration",
  "name": "My Integration",
  "bluetooth": [...],
  "codeowners": ["@username"],
  "config_flow": true,
  "dependencies": ["bluetooth"],
  "documentation": "https://...",
  "iot_class": "local_polling",
  "issue_tracker": "https://...",
  "requirements": ["bleak>=0.21.0"],
  "version": "1.0.0"
}
```

## Bluetooth Integration Testing

Bluetooth integrations depend on `bluetooth` -> `usb` -> hardware.

**CI will fail** because there's no USB/Bluetooth hardware.

**Solutions:**
1. Remove integration tests, keep only unit tests (parser, utility functions)
2. Mark integration tests as `@pytest.mark.xfail`
3. Skip tests conditionally when bluetooth setup fails

**Recommended:** Keep unit tests for parsers/protocols, remove tests that require full integration setup.

## CI Workflow Template

```yaml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check .
      - run: ruff format --check .

  hassfest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: home-assistant/actions/hassfest@master

  pytest:
    runs-on: ubuntu-latest
    needs: [lint]
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements-dev.txt
      - run: pytest
```

## Quick Reference Commands

```bash
# Lint and format
ruff check . --fix && ruff format .

# Run tests
pytest -v

# Check CI status
gh pr checks <PR_NUMBER>

# View failed CI logs
gh run view <RUN_ID> --log-failed
```

## Files Checklist for Production-Ready Integration

```
custom_components/my_integration/
├── __init__.py          # async_setup_entry, async_unload_entry
├── config_flow.py       # ConfigFlow + OptionsFlow
├── coordinator.py       # DataUpdateCoordinator
├── const.py             # Constants
├── diagnostics.py       # Diagnostics with redaction
├── entity.py            # Shared entity helpers
├── manifest.json        # Properly ordered keys
├── strings.json         # Config flow strings
├── services.yaml        # Service definitions (if any)
├── translations/
│   └── en.json          # Full translations
├── icon.png             # 256x256
└── logo.png             # 256x256
```

## Review Priority Order

1. **Tier 1 (Must-fix):** Type errors, deprecated APIs, missing manifests, blocking bugs
2. **Tier 2 (Should-fix):** Reconnect logic, error handling, diagnostics, options flow
3. **Tier 3 (Polish):** Documentation, CI, translations, icons
