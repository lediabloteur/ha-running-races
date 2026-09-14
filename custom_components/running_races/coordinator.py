"""DataUpdateCoordinator for Running Races."""
from datetime import timedelta, datetime
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, CONF_DEPARTMENT, DEFAULT_DEPARTMENT

_LOGGER = logging.getLogger(__name__)

# Official regional races database (Vienne 86 & Poitou)
RACES_DB = [
    {
        "id": "urban_trail_poitiers_2026",
        "name": "Urban Trail de Poitiers",
        "date": "2026-09-12",
        "time": "19:00",
        "distance": "10 km",
        "elevation": "+150m",
        "location": "Poitiers (86)",
        "type": "Urban Trail",
        "url": "https://www.poitiers-trail.fr"
    },
    {
        "id": "foulees_vouneuil_2026",
        "name": "Foulées de Vouneuil",
        "date": "2026-09-27",
        "time": "09:30",
        "distance": "10 km & 5 km",
        "elevation": "+40m",
        "location": "Vouneuil-sous-Biard (86)",
        "type": "Course sur Route",
        "url": "https://foulees-vouneuil.fr"
    },
    {
        "id": "trail_val_vienne_2026",
        "name": "Trail du Val de Vienne",
        "date": "2026-10-11",
        "time": "09:00",
        "distance": "15 km & 25 km",
        "elevation": "+350m",
        "location": "L'Isle-Jourdain (86)",
        "type": "Trail",
        "url": "https://cdchs86.fr"
    },
    {
        "id": "marathon_poitiers_futuroscope_2027",
        "name": "Marathon Poitiers-Futuroscope",
        "date": "2027-05-23",
        "time": "08:30",
        "distance": "42.195 km & Semi-Marathon",
        "elevation": "+120m",
        "location": "Poitiers -> Futuroscope (86)",
        "type": "Marathon Officiel",
        "url": "https://www.marathon-poitiers-futuroscope.com"
    }
]

class RunningRacesDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching regional races."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.department = entry.data.get(CONF_DEPARTMENT, DEFAULT_DEPARTMENT)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=12),
        )

    def _sync_fetch_races(self):
        """Fetch/filter races."""
        now = datetime.now()
        upcoming = []
        for r in RACES_DB:
            dt = datetime.strptime(f"{r['date']} {r['time']}", "%Y-%m-%d %H:%M")
            days_left = (dt.date() - now.date()).days
            r_copy = dict(r)
            r_copy["datetime"] = dt
            r_copy["days_remaining"] = days_left
            upcoming.append(r_copy)

        upcoming.sort(key=lambda x: x["datetime"])
        return {
            "races": upcoming,
            "next_race": next((x for x in upcoming if x["days_remaining"] >= 0), None)
        }

    async def _async_update_data(self):
        return await self.hass.async_add_executor_job(self._sync_fetch_races)
