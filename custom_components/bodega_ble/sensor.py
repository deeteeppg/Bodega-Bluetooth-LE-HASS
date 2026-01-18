"""Sensor platform for Bodega BLE fridges.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    KEY_BATTERY_PERCENT,
    KEY_BATTERY_SAVER,
    KEY_BATTERY_VOLTAGE,
    KEY_BLE_STATUS,
    KEY_COMPRESSOR_STATUS,
    KEY_LEFT_CURRENT,
    KEY_LEFT_RET_DIFF,
    KEY_LEFT_TARGET,
    KEY_LEFT_TC_COLD,
    KEY_LEFT_TC_HALT,
    KEY_LEFT_TC_HOT,
    KEY_LEFT_TC_MID,
    KEY_RIGHT_CURRENT,
    KEY_RIGHT_RET_DIFF,
    KEY_RIGHT_TARGET,
    KEY_RIGHT_TC_COLD,
    KEY_RIGHT_TC_HALT,
    KEY_RIGHT_TC_HOT,
    KEY_RIGHT_TC_MID,
    KEY_RUN_MODE,
    KEY_RUNNING_STATUS,
    KEY_START_DELAY,
    KEY_TEMP_MAX,
    KEY_TEMP_MIN,
    KEY_TEMP_UNIT,
)
from .coordinator import BodegaBleCoordinator
from .entity import device_info_for_entry


@dataclass(frozen=True, kw_only=True)
class BodegaSensorEntityDescription(SensorEntityDescription):
    """Describe Bodega BLE sensor entities."""

    data_key: str
    use_temp_unit: bool = False


SENSOR_DESCRIPTIONS: tuple[BodegaSensorEntityDescription, ...] = (
    BodegaSensorEntityDescription(
        key=KEY_LEFT_CURRENT,
        data_key=KEY_LEFT_CURRENT,
        name="Fridge temperature",
        translation_key="fridge_current",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_RIGHT_CURRENT,
        data_key=KEY_RIGHT_CURRENT,
        name="Freezer temperature",
        translation_key="freezer_current",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_LEFT_TARGET,
        data_key=KEY_LEFT_TARGET,
        name="Fridge target",
        translation_key="fridge_target",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_RIGHT_TARGET,
        data_key=KEY_RIGHT_TARGET,
        name="Freezer target",
        translation_key="freezer_target",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_TEMP_MAX,
        data_key=KEY_TEMP_MAX,
        name="Max temperature",
        translation_key="temp_max",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_TEMP_MIN,
        data_key=KEY_TEMP_MIN,
        name="Min temperature",
        translation_key="temp_min",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_LEFT_RET_DIFF,
        data_key=KEY_LEFT_RET_DIFF,
        name="Fridge hysteresis",
        translation_key="fridge_hysteresis",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_RIGHT_RET_DIFF,
        data_key=KEY_RIGHT_RET_DIFF,
        name="Freezer hysteresis",
        translation_key="freezer_hysteresis",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_START_DELAY,
        data_key=KEY_START_DELAY,
        name="Start delay",
        translation_key="start_delay",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BodegaSensorEntityDescription(
        key=KEY_LEFT_TC_HOT,
        data_key=KEY_LEFT_TC_HOT,
        name="Fridge TC hot",
        translation_key="fridge_tc_hot",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_LEFT_TC_MID,
        data_key=KEY_LEFT_TC_MID,
        name="Fridge TC mid",
        translation_key="fridge_tc_mid",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_LEFT_TC_COLD,
        data_key=KEY_LEFT_TC_COLD,
        name="Fridge TC cold",
        translation_key="fridge_tc_cold",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_LEFT_TC_HALT,
        data_key=KEY_LEFT_TC_HALT,
        name="Fridge TC halt",
        translation_key="fridge_tc_halt",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_RIGHT_TC_HOT,
        data_key=KEY_RIGHT_TC_HOT,
        name="Freezer TC hot",
        translation_key="freezer_tc_hot",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_RIGHT_TC_MID,
        data_key=KEY_RIGHT_TC_MID,
        name="Freezer TC mid",
        translation_key="freezer_tc_mid",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_RIGHT_TC_COLD,
        data_key=KEY_RIGHT_TC_COLD,
        name="Freezer TC cold",
        translation_key="freezer_tc_cold",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_RIGHT_TC_HALT,
        data_key=KEY_RIGHT_TC_HALT,
        name="Freezer TC halt",
        translation_key="freezer_tc_halt",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        use_temp_unit=True,
    ),
    BodegaSensorEntityDescription(
        key=KEY_BATTERY_PERCENT,
        data_key=KEY_BATTERY_PERCENT,
        name="Battery",
        translation_key="battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BodegaSensorEntityDescription(
        key=KEY_BATTERY_VOLTAGE,
        data_key=KEY_BATTERY_VOLTAGE,
        name="Battery voltage",
        translation_key="battery_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BodegaSensorEntityDescription(
        key=KEY_RUNNING_STATUS,
        data_key=KEY_RUNNING_STATUS,
        name="Running status",
        translation_key="running_status",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BodegaSensorEntityDescription(
        key=KEY_RUN_MODE,
        data_key=KEY_RUN_MODE,
        name="Run mode",
        translation_key="run_mode",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BodegaSensorEntityDescription(
        key=KEY_BATTERY_SAVER,
        data_key=KEY_BATTERY_SAVER,
        name="Battery saver",
        translation_key="battery_saver",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BodegaSensorEntityDescription(
        key=KEY_TEMP_UNIT,
        data_key=KEY_TEMP_UNIT,
        name="Temperature unit",
        translation_key="temp_unit",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BodegaSensorEntityDescription(
        key=KEY_COMPRESSOR_STATUS,
        data_key=KEY_COMPRESSOR_STATUS,
        name="Compressor status",
        translation_key="compressor_status",
    ),
    BodegaSensorEntityDescription(
        key=KEY_BLE_STATUS,
        data_key=KEY_BLE_STATUS,
        name="BLE status",
        translation_key="ble_status",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bodega BLE sensors."""
    coordinator: BodegaBleCoordinator = entry.runtime_data

    async_add_entities(
        BodegaBleSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class BodegaBleSensor(CoordinatorEntity[BodegaBleCoordinator], SensorEntity):
    """Representation of a Bodega BLE sensor."""

    entity_description: BodegaSensorEntityDescription

    def __init__(
        self,
        coordinator: BodegaBleCoordinator,
        entry,
        description: BodegaSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
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
    def native_unit_of_measurement(self) -> str | None:
        if self.entity_description.use_temp_unit:
            return self.hass.config.units.temperature_unit
        return self.entity_description.native_unit_of_measurement

    @property
    def native_value(self) -> str | int | float | None:
        if self.entity_description.key == KEY_BLE_STATUS:
            data = self.coordinator.data or {}
            return data.get(KEY_BLE_STATUS, "Unknown")

        data = self.coordinator.data or {}
        return data.get(self.entity_description.data_key)

    @property
    def available(self) -> bool:
        if self.entity_description.key == KEY_BLE_STATUS:
            return True
        return super().available
