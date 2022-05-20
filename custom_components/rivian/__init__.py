"""Rivian (Unofficial)"""

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup(
    hass: HomeAssistant, config_entry: ConfigEntry
):  # pylint: disable=unused-argument
    """Disallow configuration via YAML."""
    return True