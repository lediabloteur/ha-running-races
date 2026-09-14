"""DataUpdateCoordinator for Running Races integration via Miles Republic."""
from datetime import datetime, timedelta
import logging
import time
import requests

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    MILES_TOKEN_URL,
    MILES_SEARCH_URL,
    CONF_DEPARTMENTS,
    CONF_DEPARTMENT,
    CONF_SPORTS,
    DEFAULT_DEPARTMENTS,
    DEFAULT_DEPARTMENT,
    DEFAULT_SPORTS,
    FRENCH_DEPARTMENTS,
    AVAILABLE_SPORTS,
)

_LOGGER = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class MilesRepublicClient:
    """API client for Miles Republic Meilisearch backend."""

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": USER_AGENT,
            "Origin": "https://fr.milesrepublic.com",
            "Referer": "https://fr.milesrepublic.com/les-courses",
        })
        self._token: str | None = None
        self._expires_at: int = 0

    def _get_valid_token(self) -> str:
        """Fetch or refresh the Bearer search token."""
        now_ms = int(time.time() * 1000)
        if self._token and now_ms < (self._expires_at - 30000):
            return self._token

        try:
            resp = self._session.post(MILES_TOKEN_URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            self._token = data["token"]
            self._expires_at = data.get("expiresAt", now_ms + 3600000)
            return self._token
        except Exception as err:
            _LOGGER.error("Failed to obtain search token from Miles Republic: %s", err)
            raise

    def fetch_events(self, department_names: list[str], sports_keys: list[str]) -> list[dict]:
        """Fetch upcoming events for given departments and sports."""
        token = self._get_valid_token()
        now_ts = int(time.time())

        # Construct filter string
        filter_parts = [f"editionLiveStartDateTimestamp >= {now_ts}"]

        # Department filter
        if department_names:
            dept_filters = [
                f"eventCountrySubdivisionNameLevel2 = '{dept.replace(chr(39), chr(92) + chr(39))}'"
                for dept in department_names
            ]
            if len(dept_filters) == 1:
                filter_parts.append(dept_filters[0])
            else:
                filter_parts.append(f"({' OR '.join(dept_filters)})")

        # Sports filter
        if sports_keys:
            sports_filters = [
                f"editionLiveLevel1CategoryKey = '{s}'" for s in sports_keys
            ]
            if len(sports_filters) == 1:
                filter_parts.append(sports_filters[0])
            else:
                filter_parts.append(f"({' OR '.join(sports_filters)})")

        final_filter = " AND ".join(filter_parts)
        _LOGGER.debug("Querying Miles Republic with filter: %s", final_filter)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "q": "",
            "limit": 100,
            "filter": final_filter,
            "sort": ["editionLiveStartDateTimestamp:asc"],
        }

        try:
            resp = self._session.post(
                MILES_SEARCH_URL,
                headers=headers,
                json=payload,
                timeout=15,
            )
            # If token expired unexpectedly, retry once
            if resp.status_code in (401, 403):
                self._token = None
                self._expires_at = 0
                token = self._get_valid_token()
                headers["Authorization"] = f"Bearer {token}"
                resp = self._session.post(
                    MILES_SEARCH_URL,
                    headers=headers,
                    json=payload,
                    timeout=15,
                )

            resp.raise_for_status()
            data = resp.json()
            return data.get("hits", [])
        except Exception as err:
            _LOGGER.error("Error querying Miles Republic Meilisearch: %s", err)
            raise


class RunningRacesDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching regional races from Miles Republic."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.client = MilesRepublicClient()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=6),
        )

    def _resolve_department_names(self) -> list[str]:
        """Convert configured department codes/names into standardized department names."""
        # Check options first, then data
        raw_depts = self.entry.options.get(
            CONF_DEPARTMENTS,
            self.entry.options.get(
                CONF_DEPARTMENT,
                self.entry.data.get(
                    CONF_DEPARTMENTS,
                    self.entry.data.get(CONF_DEPARTMENT, DEFAULT_DEPARTMENTS),
                ),
            ),
        )

        dept_list = raw_depts if isinstance(raw_depts, list) else [str(raw_depts)]
        resolved = []

        for item in dept_list:
            item_clean = str(item).strip()
            # If formatted like "86 - Vienne", take the code
            if " - " in item_clean:
                code = item_clean.split(" - ")[0].strip()
            else:
                code = item_clean

            # Check if it matches code
            if code.upper() in FRENCH_DEPARTMENTS:
                resolved.append(FRENCH_DEPARTMENTS[code.upper()])
            elif code.zfill(2) in FRENCH_DEPARTMENTS:
                resolved.append(FRENCH_DEPARTMENTS[code.zfill(2)])
            else:
                # Check if it matches name directly
                name_match = next(
                    (name for name in FRENCH_DEPARTMENTS.values() if name.lower() == item_clean.lower()),
                    item_clean,
                )
                resolved.append(name_match)

        return list(dict.fromkeys(resolved))

    def _resolve_sports(self) -> list[str]:
        """Get configured sports keys."""
        sports = self.entry.options.get(
            CONF_SPORTS,
            self.entry.data.get(CONF_SPORTS, DEFAULT_SPORTS),
        )
        if isinstance(sports, list) and sports:
            return sports
        if isinstance(sports, str) and sports:
            return [sports]
        return DEFAULT_SPORTS

    def _sync_fetch_races(self) -> dict:
        """Fetch and parse upcoming races."""
        dept_names = self._resolve_department_names()
        sports_keys = self._resolve_sports()

        try:
            hits = self.client.fetch_events(dept_names, sports_keys)
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch races from Miles Republic: {err}") from err

        now = datetime.now()
        races = []

        for h in hits:
            try:
                start_ts = h.get("editionLiveStartDateTimestamp")
                if not start_ts:
                    continue

                dt = datetime.fromtimestamp(start_ts)
                days_left = (dt.date() - now.date()).days

                distances_raw = h.get("eventLiveDistanceKm") or []
                if isinstance(distances_raw, list) and distances_raw:
                    dist_str = ", ".join(f"{d:g} km" for d in distances_raw)
                else:
                    dist_str = "Distance non précisée"

                elevation = h.get("maxPositiveElevation")
                elev_str = f"+{elevation}m" if elevation else ""

                city = h.get("eventCity") or "Ville inconnue"
                dept_code = h.get("eventCountrySubdivisionDisplayCodeLevel2") or ""
                dept_name = h.get("eventCountrySubdivisionNameLevel2") or ""
                loc_str = f"{city} ({dept_code})" if dept_code else city

                categories_fr = h.get("editionLiveLevel1CategoryTranslation") or []
                type_str = ", ".join(categories_fr) if categories_fr else "Course"

                slug = h.get("eventSlug")
                url = f"https://fr.milesrepublic.com/event/{slug}" if slug else "https://fr.milesrepublic.com"

                price = h.get("eventLivePriceStartingFrom")

                races.append({
                    "id": str(h.get("objectID") or slug),
                    "name": h.get("eventName") or "Course",
                    "date": dt.strftime("%Y-%m-%d"),
                    "time": dt.strftime("%H:%M"),
                    "datetime": dt,
                    "days_remaining": days_left,
                    "distance": dist_str,
                    "distances_list": distances_raw,
                    "elevation": elev_str,
                    "location": loc_str,
                    "city": city,
                    "department_code": dept_code,
                    "department_name": dept_name,
                    "type": type_str,
                    "categories": h.get("editionLiveLevel1CategoryKey") or [],
                    "sub_categories": h.get("editionLiveLevel2CategoryTranslation") or [],
                    "price": price,
                    "url": url,
                    "cover_image": h.get("eventCoverImage"),
                })
            except Exception as e:
                _LOGGER.debug("Skipping event parse error: %s", e)

        races.sort(key=lambda x: x["datetime"])
        next_race = races[0] if races else None

        return {
            "races": races,
            "next_race": next_race,
            "total_count": len(races),
            "departments": dept_names,
            "sports": sports_keys,
        }

    async def _async_update_data(self):
        return await self.hass.async_add_executor_job(self._sync_fetch_races)
