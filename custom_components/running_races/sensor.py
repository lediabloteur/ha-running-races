"""Sensor platform for next running race."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NextRunningRaceSensor(coordinator, entry)])

class NextRunningRaceSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = "Prochaine Course Officielle"
        self._attr_unique_id = f"{entry.entry_id}_next_race"
        self._attr_icon = "mdi:medal"

    @property
    def native_value(self):
        nr = self.coordinator.data.get("next_race")
        if nr:
            return nr.get("name")
        return "Aucune course programmée"

    @property
    def extra_state_attributes(self):
        nr = self.coordinator.data.get("next_race")
        if nr:
            return {
                "date": nr.get("date"),
                "time": nr.get("time"),
                "distance": nr.get("distance"),
                "elevation": nr.get("elevation"),
                "location": nr.get("location"),
                "type": nr.get("type"),
                "days_remaining": nr.get("days_remaining"),
                "url": nr.get("url")
            }
        return {}
