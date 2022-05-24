"""Config flow for Rivian (Unofficial) integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import asyncio
import aiohttp

from .rivian import Rivian

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_USERNAME, CONF_PASSWORD

from .const import DEFAULT_CACHEDB, DOMAIN, _LOGGER

CONF_OTP = "Verification Code"

class RivianFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Abode."""

    VERSION = 1

    def __init__(self) -> None:
        self.data_schema = {
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_CLIENT_ID): str,
            vol.Required(CONF_CLIENT_SECRET): str,
        }
        self.otp_data_schema = {
            vol.Required(CONF_OTP): str,
        }
        self._username: str | None = None
        self._password: str | None = None
        self._mfa_code: str | None = None
        self._rivian: Rivian | None = None

    async def _async_rivian_login(self, step_id: str) -> FlowResult:
        """Handle login with Rivian."""
        errors = {}
        try:
            self._rivian = Rivian(self._client_id, self._client_secret)
            login_info = await self._rivian.authenticate(self._username, self._password)
            _LOGGER.info(login_info)
        except Exception as ex:
            _LOGGER.error(ex)
            errors = {"base": "cannot_connect"}

        if errors:
            return self.async_show_form(
                step_id=step_id, data_schema=vol.Schema(self.data_schema), errors=errors
            )

        if login_info["session_token"]:
            self._session_token = login_info["session_token"]
            return await self.async_step_mfa()

        return await self._async_create_entry()

    async def _async_rivian_otp_login(self) -> FlowResult:
        """Handle otp with Rivian."""
        errors = {}
        try:
            self._rivian = Rivian(self._client_id, self._client_secret)
            login_info = await self._rivian.validate_otp(self._username, self._mfa_code, self._session_token)
            _LOGGER.info(login_info)
        except Exception as ex:
            _LOGGER.error(ex)
            errors = {"base": "cannot_connect"}

        if errors:
            return self.async_show_form(
                step_id="mfa", data_schema=vol.Schema(self.otp_data_schema), errors=errors
            )

        if login_info["access_token"]:
            self._access_token = login_info["access_token"]

        if login_info["refresh_token"]:
            self._refresh_token = login_info["refresh_token"]

        return await self._async_create_entry()

    async def _async_create_entry(self) -> FlowResult:
        """Create the config entry."""
        config_data = {
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
        }

        return self.async_create_entry(
            title="Rivian (Unofficial)", data=config_data
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=vol.Schema(self.data_schema)
            )

        self._username = user_input[CONF_USERNAME]
        self._password = user_input[CONF_PASSWORD]
        self._client_id = user_input[CONF_CLIENT_ID]
        self._client_secret = user_input[CONF_CLIENT_SECRET]

        return await self._async_rivian_login(step_id="user")

    async def async_step_mfa(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a multi-factor authentication (MFA) flow."""
        if user_input is None:
            return self.async_show_form(
                step_id="mfa", data_schema=vol.Schema(self.otp_data_schema)
            )

        self._mfa_code = user_input[CONF_OTP]

        return await self._async_rivian_otp_login()

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
