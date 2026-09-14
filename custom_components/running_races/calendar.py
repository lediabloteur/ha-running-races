"""Calendar platform for Running Races."""
from datetime import datetime, timedelta
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
        local_tz = dt_util.get_default_time_zone()

        for r in races:
            try:
                dt_raw = datetime.strptime(f"{r['date']} {r['time']}", "%Y-%m-%d %H:%M")
                start_dt = dt_raw.replace(tzinfo=local_tz)
                end_dt = start_dt + timedelta(hours=3)

                events.append(CalendarEvent(
                    start=start_dt,
                    end=end_dt,
                    summary=f"{r['name']} ({r['distance']})",
                    description=f"{r['type']} · Dénivelé {r['elevation']} · {r['location']}\nInfos & Inscription: {r['url']}",
                    location=r["location"]
                ))
            except Exception:
                pass
        return sorted(events, key=lambda x: x.start)

    @property
    def event(self) -> CalendarEvent | None:
        now = dt_util.now()
        events = self._get_events()
        for e in events:
            if e.end >= now:
                return e
        return None

    async def async_get_events(self, hass: HomeAssistant, start_date: datetime, end_date: datetime) -> list[CalendarEvent]:
        events = self._get_events()
        start_tz = start_date if start_date.tzinfo else start_date.replace(tzinfo=dt_util.get_default_time_zone())
        end_tz = end_date if end_date.tzinfo else end_date.replace(tzinfo=dt_util.get_default_time_zone())
        return [e for e in events if start_tz <= e.end and e.start <= end_tz]
