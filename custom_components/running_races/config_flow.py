"""Config flow and Options flow for Running Races (Miles Republic)."""
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_DEPARTMENTS,
    CONF_DEPARTMENT,
    CONF_SPORTS,
    DEFAULT_DEPARTMENTS,
    DEFAULT_SPORTS,
    FRENCH_DEPARTMENTS,
    AVAILABLE_SPORTS,
)


def _get_department_options() -> list[selector.SelectOptionDict]:
    return [
        selector.SelectOptionDict(value=code, label=f"{code} - {name}")
        for code, name in FRENCH_DEPARTMENTS.items()
    ]


def _get_sports_options() -> list[selector.SelectOptionDict]:
    return [
        selector.SelectOptionDict(value=key, label=label)
        for key, label in AVAILABLE_SPORTS.items()
    ]


class RunningRacesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Running Races."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            depts = user_input.get(CONF_DEPARTMENTS, DEFAULT_DEPARTMENTS)
            if isinstance(depts, str):
                depts = [depts]
            depts_str = ", ".join(depts)
            return self.async_create_entry(
                title=f"Courses ({depts_str})",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_DEPARTMENTS,
                    default=DEFAULT_DEPARTMENTS,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=_get_department_options(),
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(
                    CONF_SPORTS,
                    default=DEFAULT_SPORTS,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=_get_sports_options(),
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return RunningRacesOptionsFlowHandler()


class RunningRacesOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Running Races."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current configured values
        curr_depts = self.config_entry.options.get(
            CONF_DEPARTMENTS,
            self.config_entry.options.get(
                CONF_DEPARTMENT,
                self.config_entry.data.get(
                    CONF_DEPARTMENTS,
                    self.config_entry.data.get(CONF_DEPARTMENT, DEFAULT_DEPARTMENTS),
                ),
            ),
        )
        if isinstance(curr_depts, str):
            curr_depts = [curr_depts]

        curr_sports = self.config_entry.options.get(
            CONF_SPORTS,
            self.config_entry.data.get(CONF_SPORTS, DEFAULT_SPORTS),
        )
        if isinstance(curr_sports, str):
            curr_sports = [curr_sports]

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_DEPARTMENTS,
                    default=curr_depts,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=_get_department_options(),
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(
                    CONF_SPORTS,
                    default=curr_sports,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=_get_sports_options(),
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
