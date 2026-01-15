"""Button platform for Bodega BLE fridges.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BodegaBleCoordinator


@dataclass(frozen=True, kw_only=True)
class BodegaButtonEntityDescription(ButtonEntityDescription):
    """Describe Bodega BLE button entities."""

    action_key: str


BUTTON_DESCRIPTIONS: tuple[BodegaButtonEntityDescription, ...] = (
    BodegaButtonEntityDescription(
        key="bind",
        action_key="bind",
        name="Bind",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities,
) -> None:
    """Set up Bodega BLE buttons."""
    coordinator: BodegaBleCoordinator = entry.runtime_data

    async_add_entities(
        BodegaBleButton(coordinator, entry, description)
        for description in BUTTON_DESCRIPTIONS
    )


class BodegaBleButton(CoordinatorEntity[BodegaBleCoordinator], ButtonEntity):
    """Representation of a Bodega BLE button."""

    entity_description: BodegaButtonEntityDescription

    def __init__(
        self,
        coordinator: BodegaBleCoordinator,
        entry,
        description: BodegaButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._device_name = entry.title
        self._address = entry.data["address"]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._address)},
            connections={(CONNECTION_BLUETOOTH, self._address)},
            name=self._device_name,
            manufacturer="DeeTeePPG",
            model="BLE Fridge",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_send_bind()
        await self.coordinator.async_request_refresh()
