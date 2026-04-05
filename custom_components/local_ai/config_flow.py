"""Config flow for Local AI."""
import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from . import DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("url", default="http://localhost:11434"): str,
        vol.Required("model", default="llama3.2"): str,
    }
)


async def _validate_input(hass: HomeAssistant, data: dict) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{data['url'].rstrip('/')}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as resp:
            resp.raise_for_status()


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                await _validate_input(self.hass, user_input)
                return self.async_create_entry(title="Local AI", data=user_input)
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
