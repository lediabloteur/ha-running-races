"""Calendar platform for Running Races."""
from datetime import datetime, timedelta
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RunningRacesCalendarEntity(coordinator, entry)])

class RunningRacesCalendarEntity(CoordinatorEntity, CalendarEntity):
    """Representation of Running Races Calendar."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        dept = entry.data.get("department", "86")
        self._attr_name = f"Courses & Trails ({dept})"
        self._attr_unique_id = f"{entry.entry_id}_calendar"
        self._attr_icon = "mdi:medal-outline"

    @property
    def event(self) -> CalendarEvent | None:
        races = self.coordinator.data.get("races", [])
        now = datetime.now()
        for r in races:
            dt = r["datetime"]
            if dt >= now:
                return CalendarEvent(
                    start=dt,
                    end=dt + timedelta(hours=3),
                    summary=f"{r['name']} ({r['distance']})",
                    description=f"{r['type']} · Dénivelé {r['elevation']} · {r['location']}\nInfos & Inscription: {r['url']}",
                    location=r["location"]
                )
        return None

    async def async_get_events(self, hass: HomeAssistant, start_date: datetime, end_date: datetime) -> list[CalendarEvent]:
        events = []
        for r in self.coordinator.data.get("races", []):
            dt = r["datetime"]
            end_dt = dt + timedelta(hours=3)
            if start_date <= end_dt and dt <= end_date:
                events.append(CalendarEvent(
                    start=dt,
                    end=end_dt,
                    summary=f"{r['name']} ({r['distance']})",
                    description=f"{r['type']} · Dénivelé {r['elevation']} · {r['location']}\nInfos & Inscription: {r['url']}",
                    location=r["location"]
                ))
        return events
