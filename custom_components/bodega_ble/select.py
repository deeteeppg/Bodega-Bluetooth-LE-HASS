"""Select platform for Bodega BLE fridges.

Provides select entities for:
- Temperature Unit: Choose between Celsius and Fahrenheit display
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import KEY_TEMP_UNIT
from .coordinator import BodegaBleCoordinator
from .entity import device_info_for_entry

TEMP_UNIT_OPTIONS = ["Celsius", "Fahrenheit"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bodega BLE select entities."""
    coordinator: BodegaBleCoordinator = entry.runtime_data

    async_add_entities([BodegaTempUnitSelect(coordinator, entry)])


class BodegaTempUnitSelect(CoordinatorEntity[BodegaBleCoordinator], SelectEntity):
    """Select entity for temperature unit."""

    _attr_has_entity_name = True
    _attr_name = "Temperature unit"
    _attr_translation_key = "temp_unit_select"
    _attr_options = TEMP_UNIT_OPTIONS

    def __init__(
        self,
        coordinator: BodegaBleCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temp_unit_select"
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for this entity."""
        return device_info_for_entry(self._entry)

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        data = self.coordinator.data or {}
        unit = data.get(KEY_TEMP_UNIT)
        if unit == "F":
            return "Fahrenheit"
        if unit == "C":
            return "Celsius"
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        fahrenheit = option == "Fahrenheit"
        await self.coordinator.async_set_temp_unit(fahrenheit)
        await self.coordinator.async_request_refresh()
