"""Binary sensor platform for Bodega BLE fridges.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import KEY_LOCKED, KEY_POWERED
from .coordinator import BodegaBleCoordinator
from .entity import device_info_for_entry


@dataclass(frozen=True, kw_only=True)
class BodegaBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe Bodega BLE binary sensor entities."""

    data_key: str


BINARY_SENSOR_DESCRIPTIONS: tuple[BodegaBinarySensorEntityDescription, ...] = (
    BodegaBinarySensorEntityDescription(
        key=KEY_LOCKED,
        data_key=KEY_LOCKED,
        name="Locked",
        device_class=BinarySensorDeviceClass.LOCK,
    ),
    BodegaBinarySensorEntityDescription(
        key=KEY_POWERED,
        data_key=KEY_POWERED,
        name="Powered",
        device_class=BinarySensorDeviceClass.POWER,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities,
) -> None:
    """Set up Bodega BLE binary sensors."""
    coordinator: BodegaBleCoordinator = entry.runtime_data

    async_add_entities(
        BodegaBleBinarySensor(coordinator, entry, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class BodegaBleBinarySensor(
    CoordinatorEntity[BodegaBleCoordinator], BinarySensorEntity
):
    """Representation of a Bodega BLE binary sensor."""

    entity_description: BodegaBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: BodegaBleCoordinator,
        entry,
        description: BodegaBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for this entity."""
        return device_info_for_entry(self._entry)

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data or {}
        return data.get(self.entity_description.data_key)
