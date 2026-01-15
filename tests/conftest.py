"""Fixtures for bodega_ble tests."""
from __future__ import annotations

import sys
from pathlib import Path

from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.bodega_ble.const import DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for tests."""
    yield


@pytest.fixture(autouse=True)
def mock_bluetooth_history():
    """Avoid platform bluetooth history lookups during tests."""
    history_mock = AsyncMock(return_value=({}, {}))
    with (
        patch(
            "homeassistant.components.bluetooth.util.async_load_history_from_system",
            new=history_mock,
        ),
        patch(
            "homeassistant.components.bluetooth.manager.async_load_history_from_system",
            new=lambda *args, **kwargs: ({}, {}),
        ),
    ):
        yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test Fridge",
        data={"address": "AA:BB:CC:DD:EE:FF"},
        unique_id="AA:BB:CC:DD:EE:FF",
    )
