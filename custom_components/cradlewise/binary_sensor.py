"""Binary sensor platform for Cradlewise."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cradlewise binary sensors."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    status_coord = coordinators["status"]

    async_add_entities([
        CradlewiseInCribBinarySensor(status_coord, entry),
        CradlewiseBounceBinarySensor(status_coord, entry),
        CradlewiseMusicBinarySensor(status_coord, entry),
    ])

class CradlewiseInCribBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Presence sensor for baby in crib."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = "Cradlewise Baby in Crib"
        self._attr_unique_id = f"{entry.entry_id}_is_in_crib"
        self._attr_device_class = BinarySensorDeviceClass.PRESENCE

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get("is_in_crib") if self.coordinator.data else None

class CradlewiseBounceBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Sensor for crib bouncing/rocking state."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = "Cradlewise Bounce Active"
        self._attr_unique_id = f"{entry.entry_id}_bounce_active"
        self._attr_icon = "mdi:arrow-up-down"

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data and "crib_mode" in self.coordinator.data:
            return self.coordinator.data["crib_mode"].get("bounce") == "on"
        return None

class CradlewiseMusicBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Sensor for crib music state."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = "Cradlewise Music Active"
        self._attr_unique_id = f"{entry.entry_id}_music_active"
        self._attr_icon = "mdi:music"

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data and "crib_mode" in self.coordinator.data:
            return self.coordinator.data["crib_mode"].get("music") == "on"
        return None
