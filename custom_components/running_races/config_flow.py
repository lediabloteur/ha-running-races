"""Config flow for Running Races."""
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_DEPARTMENT, DEFAULT_DEPARTMENT

class RunningRacesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            dept = user_input.get(CONF_DEPARTMENT, DEFAULT_DEPARTMENT)
            return self.async_create_entry(title=f"Courses ({dept})", data=user_input)

        schema = vol.Schema({
            vol.Optional(CONF_DEPARTMENT, default=DEFAULT_DEPARTMENT): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema)
