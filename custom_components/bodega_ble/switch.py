"""Switch platform for Bodega BLE fridges.

Provides controllable switch entities for:
- Lock: Enable/disable physical button controls
- Power: Turn the fridge on/off
- Temperature Unit: Switch between Celsius and Fahrenheit display
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import KEY_LOCKED, KEY_POWERED
from .coordinator import BodegaBleCoordinator
from .entity import device_info_for_entry


@dataclass(frozen=True, kw_only=True)
class BodegaSwitchEntityDescription(SwitchEntityDescription):
    """Describe Bodega BLE switch entities."""

    data_key: str
    turn_on_fn: Callable[[BodegaBleCoordinator], Awaitable[None]]
    turn_off_fn: Callable[[BodegaBleCoordinator], Awaitable[None]]
    value_fn: Callable[[dict[str, Any]], bool | None]


async def _set_lock_on(coordinator: BodegaBleCoordinator) -> None:
    # Switch ON = Controls UNLOCKED (lock disabled)
    await coordinator.async_set_lock(False)


async def _set_lock_off(coordinator: BodegaBleCoordinator) -> None:
    # Switch OFF = Controls LOCKED (lock enabled)
    await coordinator.async_set_lock(True)


async def _set_power_on(coordinator: BodegaBleCoordinator) -> None:
    await coordinator.async_set_power(True)


async def _set_power_off(coordinator: BodegaBleCoordinator) -> None:
    await coordinator.async_set_power(False)


def _get_controls_enabled(data: dict[str, Any]) -> bool | None:
    """Return True if controls are enabled (not locked)."""
    locked = data.get(KEY_LOCKED)
    if locked is None:
        return None
    return not locked  # Invert: switch ON = controls enabled (not locked)


def _get_powered(data: dict[str, Any]) -> bool | None:
    return data.get(KEY_POWERED)


SWITCH_DESCRIPTIONS: tuple[BodegaSwitchEntityDescription, ...] = (
    BodegaSwitchEntityDescription(
        key="control_lock",
        data_key=KEY_LOCKED,
        name="Control lock",
        translation_key="control_lock",
        turn_on_fn=_set_lock_on,
        turn_off_fn=_set_lock_off,
        value_fn=_get_controls_enabled,
    ),
    BodegaSwitchEntityDescription(
        key="power",
        data_key=KEY_POWERED,
        name="Power",
        translation_key="power",
        turn_on_fn=_set_power_on,
        turn_off_fn=_set_power_off,
        value_fn=_get_powered,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bodega BLE switches."""
    coordinator: BodegaBleCoordinator = entry.runtime_data

    async_add_entities(
        BodegaBleSwitch(coordinator, entry, description)
        for description in SWITCH_DESCRIPTIONS
    )


class BodegaBleSwitch(CoordinatorEntity[BodegaBleCoordinator], SwitchEntity):
    """Representation of a Bodega BLE switch."""

    entity_description: BodegaSwitchEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BodegaBleCoordinator,
        entry: ConfigEntry,
        description: BodegaSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for this entity."""
        return device_info_for_entry(self._entry)

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        data = self.coordinator.data or {}
        return self.entity_description.value_fn(data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self.entity_description.turn_on_fn(self.coordinator)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self.entity_description.turn_off_fn(self.coordinator)
        await self.coordinator.async_request_refresh()
