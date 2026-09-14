"""Calendar platform for Running Races (Miles Republic)."""
from datetime import datetime, timedelta, time
import logging

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from .const import DOMAIN, CONF_DEPARTMENTS, CONF_DEPARTMENT, DEFAULT_DEPARTMENTS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Running Races calendar."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RunningRacesCalendarEntity(coordinator, entry)])


class RunningRacesCalendarEntity(CoordinatorEntity, CalendarEntity):
    """Representation of Running Races Calendar."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        depts = entry.options.get(
            CONF_DEPARTMENTS,
            entry.options.get(
                CONF_DEPARTMENT,
                entry.data.get(
                    CONF_DEPARTMENTS,
                    entry.data.get(CONF_DEPARTMENT, DEFAULT_DEPARTMENTS),
                ),
            ),
        )
        depts_str = ", ".join(depts) if isinstance(depts, list) else str(depts)
        self._attr_name = f"Courses & Trails ({depts_str})"
        self._attr_unique_id = f"{entry.entry_id}_calendar"
        self._attr_icon = "mdi:medal-outline"

    def _get_events(self) -> list[CalendarEvent]:
        events = []
        if not self.coordinator.data:
            return events

        races = self.coordinator.data.get("races", [])
        tz = dt_util.DEFAULT_TIME_ZONE

        for r in races:
            try:
                dt_obj: datetime = r.get("datetime")
                if not dt_obj:
                    d = datetime.strptime(r["date"], "%Y-%m-%d").date()
                    start_dt = datetime.combine(d, time.min, tzinfo=tz)
                    end_dt = datetime.combine(d + timedelta(days=1), time.min, tzinfo=tz)
                else:
                    if dt_obj.tzinfo is None:
                        start_dt = dt_obj.replace(tzinfo=tz)
                    else:
                        start_dt = dt_obj
                    end_dt = start_dt + timedelta(hours=3)

                price_info = f"à partir de {r['price']}€" if r.get("price") else "Consulter le site"
                elev_info = r.get("elevation") or "Non spécifié"

                desc = (
                    f"🏆 {r.get('name')}\n"
                    f"📍 Lieu: {r.get('location')}\n"
                    f"📏 Distances: {r.get('distance')}\n"
                    f"⛰️ Dénivelé: {elev_info}\n"
                    f"🏷️ Disciplines: {r.get('type')}\n"
                    f"💶 Tarif: {price_info}\n"
                    f"🔗 Inscription & Infos: {r.get('url')}"
                )

                events.append(
                    CalendarEvent(
                        start=start_dt,
                        end=end_dt,
                        summary=f"{r.get('name')} ({r.get('distance')})",
                        description=desc,
                        location=r.get("location"),
                        uid=r.get("id"),
                    )
                )
            except Exception as e:
                _LOGGER.debug("Error building calendar event: %s", e)

        return sorted(events, key=lambda x: x.start)

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        now = dt_util.now()
        for e in self._get_events():
            if e.end >= now:
                return e
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return events within the requested range."""
        events = self._get_events()
        return [e for e in events if start_date <= e.end and e.start <= end_date]
