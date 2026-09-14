"""Calendar platform for Running Races."""
from datetime import datetime, date, timedelta
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

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

    def _get_events(self) -> list[CalendarEvent]:
        events = []
        races = self.coordinator.data.get("races", [])

        for r in races:
            try:
                dt = datetime.strptime(r["date"], "%Y-%m-%d").date()
                events.append(CalendarEvent(
                    start=dt,
                    end=dt + timedelta(days=1),
                    summary=f"{r['name']} ({r['distance']})",
                    description=f"{r['type']} · Dénivelé {r['elevation']} · {r['location']}\nHeure de départ: {r['time']}\nInfos: {r['url']}",
                    location=r["location"]
                ))
            except Exception:
                pass
        return sorted(events, key=lambda x: x.start)

    @property
    def event(self) -> CalendarEvent | None:
        today = dt_util.now().date()
        for e in self._get_events():
            if e.end >= today:
                return e
        return None

    async def async_get_events(self, hass: HomeAssistant, start_date: datetime, end_date: datetime) -> list[CalendarEvent]:
        events = self._get_events()
        start_d = start_date.date()
        end_d = end_date.date()
        return [e for e in events if start_d <= e.end and e.start <= end_d]
