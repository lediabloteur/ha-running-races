"""Calendar platform for Running Races."""
from datetime import datetime, timedelta, time
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
        tz = dt_util.DEFAULT_TIME_ZONE

        for r in races:
            try:
                d = datetime.strptime(r["date"], "%Y-%m-%d").date()
                start_dt = datetime.combine(d, time.min, tzinfo=tz)
                end_dt = datetime.combine(d + timedelta(days=1), time.min, tzinfo=tz)
                events.append(CalendarEvent(
                    start=start_dt,
                    end=end_dt,
                    summary=f"{r['name']} ({r['distance']})",
                    description=f"{r['type']} · Dénivelé {r['elevation']} · {r['location']}\nHeure de départ: {r['time']}\nInfos: {r['url']}",
                    location=r["location"]
                ))
            except Exception:
                pass
        return sorted(events, key=lambda x: x.start)

    @property
    def event(self) -> CalendarEvent | None:
        now = dt_util.now()
        for e in self._get_events():
            if e.end >= now:
                return e
        return None

    async def async_get_events(self, hass: HomeAssistant, start_date: datetime, end_date: datetime) -> list[CalendarEvent]:
        events = self._get_events()
        return [e for e in events if start_date <= e.end and e.start <= end_date]
