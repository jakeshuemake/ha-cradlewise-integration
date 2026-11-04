"""Config flow for Cradlewise integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import BASE_URL, CONF_API_TOKEN, DOMAIN, LOGGER

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_TOKEN): str,
    }
)

async def validate_token(session, token: str) -> dict[str, Any]:
    """Validate token using /baby/status."""
    clean_token = token.replace("Bearer ", "").strip()
    headers = {"Authorization": f"Bearer {clean_token}"}

    async with session.get(f"{BASE_URL}/baby/status", headers=headers, timeout=10) as resp:
        if resp.status in (401, 403):
            raise InvalidAuth
        elif resp.status == 429:
            raise RateLimited
        elif resp.status != 200:
            raise CannotConnect

        data = await resp.json()
        return {"token": clean_token, "status": data.get("status")}


class CradlewiseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cradlewise."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                session = async_get_clientsession(self.hass)
                info = await validate_token(session, user_input[CONF_API_TOKEN])

                # Match against the token suffix as an initial unique ID
                await self.async_set_unique_id(info["token"][-8:])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Cradlewise Crib",
                    data={CONF_API_TOKEN: info["token"]},
                )
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except RateLimited:
                errors["base"] = "rate_limited"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception as err:
                LOGGER.error("Unexpected exception: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual reconfiguration from the UI menu."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            try:
                session = async_get_clientsession(self.hass)
                info = await validate_token(session, user_input[CONF_API_TOKEN])

                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    data_updates={CONF_API_TOKEN: info["token"]},
                )
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except RateLimited:
                errors["base"] = "rate_limited"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception as err:
                LOGGER.error("Unexpected error during reconfigure: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> FlowResult:
        """Handle automated reauthentication when credentials expire."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm reauth dialog."""
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()

        if user_input is not None:
            try:
                session = async_get_clientsession(self.hass)
                info = await validate_token(session, user_input[CONF_API_TOKEN])

                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={CONF_API_TOKEN: info["token"]},
                )
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except RateLimited:
                errors["base"] = "rate_limited"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception as err:
                LOGGER.error("Unexpected error during reauth: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(Exception):
    """Error to indicate connection failure."""


class InvalidAuth(Exception):
    """Error to indicate invalid auth."""


class RateLimited(Exception):
    """Error to indicate rate limits exceeded."""
