"""Sensor platform for Cradlewise."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cradlewise sensors."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    status_coord = coordinators["status"]
    metrics_coord = coordinators["metrics"]

    async_add_entities([
        CradlewiseStatusSensor(status_coord, entry),
        CradlewiseStatusSinceSensor(status_coord, entry),
        CradlewiseTotalNightSleepSensor(metrics_coord, entry),
        CradlewiseTotalDaySleepSensor(metrics_coord, entry),
        CradlewiseLongestStretchSensor(metrics_coord, entry),
    ])

class CradlewiseStatusSensor(CoordinatorEntity, SensorEntity):
    """Main status sensor."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = "Cradlewise Baby Status"
        self._attr_unique_id = f"{entry.entry_id}_baby_status"

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get("status") if self.coordinator.data else None

    @property
    def icon(self) -> str:
        status = self.native_value
        if status == "sleeping":
            return "mdi:baby-sleep"
        elif status in ("stirring", "crying"):
            return "mdi:baby-bottle"
        elif status == "awake":
            return "mdi:baby-face"
        return "mdi:baby-carriage"

class CradlewiseStatusSinceSensor(CoordinatorEntity, SensorEntity):
    """Status timestamp sensor."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = "Cradlewise Status Since"
        self._attr_unique_id = f"{entry.entry_id}_status_since"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get("since") if self.coordinator.data else None

class CradlewiseTotalNightSleepSensor(CoordinatorEntity, SensorEntity):
    """Total night sleep duration in hours."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = "Cradlewise Total Night Sleep"
        self._attr_unique_id = f"{entry.entry_id}_total_night_sleep"
        self._attr_native_unit_of_measurement = UnitOfTime.HOURS
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:weather-night"

    @property
    def native_value(self) -> float | None:
        if not self.coordinator.data or "c_chart" not in self.coordinator.data:
            return None
        
        aggregates = self.coordinator.data["c_chart"].get("day_aggregates", {})
        if not aggregates:
            return None

        latest_day = list(aggregates.keys())[-1]
        seconds = aggregates[latest_day].get("total_night_sleep", 0)
        return round(seconds / 3600.0, 2)

class CradlewiseTotalDaySleepSensor(CoordinatorEntity, SensorEntity):
    """Total daytime nap duration in hours."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = "Cradlewise Total Day Sleep"
        self._attr_unique_id = f"{entry.entry_id}_total_day_sleep"
        self._attr_native_unit_of_measurement = UnitOfTime.HOURS
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:weather-sunny"

    @property
    def native_value(self) -> float | None:
        if not self.coordinator.data or "c_chart" not in self.coordinator.data:
            return None
        
        aggregates = self.coordinator.data["c_chart"].get("day_aggregates", {})
        if not aggregates:
            return None

        latest_day = list(aggregates.keys())[-1]
        seconds = aggregates[latest_day].get("total_day_sleep", 0)
        return round(seconds / 3600.0, 2)

class CradlewiseLongestStretchSensor(CoordinatorEntity, SensorEntity):
    """Longest stretch text from day metrics."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = "Cradlewise Longest Stretch"
        self._attr_unique_id = f"{entry.entry_id}_longest_stretch"
        self._attr_icon = "mdi:human-baby"

    @property
    def native_value(self) -> str | None:
        if not self.coordinator.data or "day_metrics" not in self.coordinator.data:
            return None

        metrics = self.coordinator.data["day_metrics"].get("metrics", [])
        if not metrics:
            return None

        banners = metrics[0].get("banners", [])
        for banner in banners:
            if banner.get("type") == "info" and "LONGEST STRETCH" in banner.get("header", "").upper():
                return banner.get("data", {}).get("display_value", "Unknown")
        
        return None
