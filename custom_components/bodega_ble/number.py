"""Number platform for Bodega BLE fridges.

Provides controllable number entities for:
- Fridge Target: Set the fridge zone target temperature
- Freezer Target: Set the freezer zone target temperature
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import KEY_LEFT_TARGET, KEY_RIGHT_TARGET
from .coordinator import BodegaBleCoordinator
from .entity import device_info_for_entry

# Temperature ranges in Celsius
FRIDGE_MIN_C = 0.0
FRIDGE_MAX_C = 10.0
FREEZER_MIN_C = -20.0
FREEZER_MAX_C = -12.0


def _c_to_f(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9.0 / 5.0) + 32.0


@dataclass(frozen=True, kw_only=True)
class BodegaNumberEntityDescription(NumberEntityDescription):
    """Describe Bodega BLE number entities."""

    data_key: str
    set_value_fn: Callable[[BodegaBleCoordinator, float], Awaitable[None]]
    min_value_c: float
    max_value_c: float


async def _set_fridge_target(
    coordinator: BodegaBleCoordinator, value: float
) -> None:
    await coordinator.async_set_left_target(value)


async def _set_freezer_target(
    coordinator: BodegaBleCoordinator, value: float
) -> None:
    await coordinator.async_set_right_target(value)


NUMBER_DESCRIPTIONS: tuple[BodegaNumberEntityDescription, ...] = (
    BodegaNumberEntityDescription(
        key="fridge_target",
        data_key=KEY_LEFT_TARGET,
        name="Fridge target",
        translation_key="fridge_target",
        device_class=NumberDeviceClass.TEMPERATURE,
        mode=NumberMode.SLIDER,
        set_value_fn=_set_fridge_target,
        min_value_c=FRIDGE_MIN_C,
        max_value_c=FRIDGE_MAX_C,
    ),
    BodegaNumberEntityDescription(
        key="freezer_target",
        data_key=KEY_RIGHT_TARGET,
        name="Freezer target",
        translation_key="freezer_target",
        device_class=NumberDeviceClass.TEMPERATURE,
        mode=NumberMode.SLIDER,
        set_value_fn=_set_freezer_target,
        min_value_c=FREEZER_MIN_C,
        max_value_c=FREEZER_MAX_C,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bodega BLE number entities."""
    coordinator: BodegaBleCoordinator = entry.runtime_data

    entities: list[BodegaBleNumber] = []
    for description in NUMBER_DESCRIPTIONS:
        # Only add freezer target if device has dual zones
        if description.data_key == KEY_RIGHT_TARGET:
            data = coordinator.data or {}
            if KEY_RIGHT_TARGET not in data:
                continue
        entities.append(BodegaBleNumber(coordinator, entry, description))

    async_add_entities(entities)


class BodegaBleNumber(CoordinatorEntity[BodegaBleCoordinator], NumberEntity):
    """Representation of a Bodega BLE number entity."""

    entity_description: BodegaNumberEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BodegaBleCoordinator,
        entry: ConfigEntry,
        description: BodegaNumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for this entity."""
        return device_info_for_entry(self._entry)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self.hass.config.units.temperature_unit

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        min_c = self.entity_description.min_value_c
        if self.hass.config.units.temperature_unit == UnitOfTemperature.FAHRENHEIT:
            return _c_to_f(min_c)
        return min_c

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        max_c = self.entity_description.max_value_c
        if self.hass.config.units.temperature_unit == UnitOfTemperature.FAHRENHEIT:
            return _c_to_f(max_c)
        return max_c

    @property
    def native_step(self) -> float:
        """Return the step value."""
        return 1.0

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        data = self.coordinator.data or {}
        return data.get(self.entity_description.data_key)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        await self.entity_description.set_value_fn(self.coordinator, value)
        await self.coordinator.async_request_refresh()
