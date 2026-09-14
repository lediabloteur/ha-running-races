"""Sensor platform for running races from Miles Republic."""
from homeassistant.components.sensor import SensorEntity
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
    """Set up the Running Races sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        NextRunningRaceSensor(coordinator, entry),
        TotalRunningRacesSensor(coordinator, entry),
    ])


class NextRunningRaceSensor(CoordinatorEntity, SensorEntity):
    """Sensor for the next upcoming running race."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = "Prochaine Course Officielle"
        self._attr_unique_id = f"{entry.entry_id}_next_race"
        self._attr_icon = "mdi:medal"

    @property
    def native_value(self) -> str:
        """Return the title of the next race."""
        if not self.coordinator.data:
            return "Chargement..."
        nr = self.coordinator.data.get("next_race")
        if nr:
            return nr.get("name", "Course sans titre")
        return "Aucune course programmée"

    @property
    def extra_state_attributes(self) -> dict:
        """Return detailed attributes for the next race and the full races list."""
        if not self.coordinator.data:
            return {}

        data = self.coordinator.data
        nr = data.get("next_race")
        races = data.get("races", [])

        # Clean races list for state attributes (no non-serializable objects)
        cleaned_races = []
        for r in races:
            cleaned_races.append({
                "id": r.get("id"),
                "name": r.get("name"),
                "date": r.get("date"),
                "time": r.get("time"),
                "distance": r.get("distance"),
                "elevation": r.get("elevation"),
                "location": r.get("location"),
                "city": r.get("city"),
                "department_code": r.get("department_code"),
                "department_name": r.get("department_name"),
                "type": r.get("type"),
                "days_remaining": r.get("days_remaining"),
                "price": r.get("price"),
                "url": r.get("url"),
                "cover_image": r.get("cover_image"),
            })

        attrs = {
            "total_available_races": len(races),
            "departments": data.get("departments", []),
            "sports": data.get("sports", []),
            "races": cleaned_races,
        }

        if nr:
            attrs.update({
                "date": nr.get("date"),
                "time": nr.get("time"),
                "distance": nr.get("distance"),
                "elevation": nr.get("elevation"),
                "location": nr.get("location"),
                "city": nr.get("city"),
                "department_code": nr.get("department_code"),
                "department_name": nr.get("department_name"),
                "type": nr.get("type"),
                "days_remaining": nr.get("days_remaining"),
                "price": nr.get("price"),
                "url": nr.get("url"),
                "cover_image": nr.get("cover_image"),
            })

        return attrs


class TotalRunningRacesSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total number of available races."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = "Courses Disponibles Total"
        self._attr_unique_id = f"{entry.entry_id}_total_races"
        self._attr_icon = "mdi:run-fast"

    @property
    def native_value(self) -> int:
        if not self.coordinator.data:
            return 0
        return self.coordinator.data.get("total_count", 0)

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        return {
            "departments": self.coordinator.data.get("departments", []),
            "sports": self.coordinator.data.get("sports", []),
        }
