"""The Rivian (Unofficial) integration."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, _LOGGER

from .rivian import Rivian

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]
UPDATE_INTERVAL = 30

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Rivian from a config entry."""
    _LOGGER.info("==== async_setup_entry ====")

    _LOGGER.info(hass.data[DOMAIN])

    # rivian_coordinator = RivianCoordinator(
    #     hass,
    # )
    # _LOGGER.info("============= rivian_coordinator =============")
    # try:
    #     await rivian_coordinator.async_validate_input()

    # except InvalidAuth as ex:
    #     raise ConfigEntryAuthFailed from ex

    # await rivian_coordinator.async_config_entry_first_refresh()

    # hass.data.setdefault(DOMAIN, {})[entry.entry_id] = rivian_coordinator

    # hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class RivianCoordinator(DataUpdateCoordinator):
    """Rivian coordinator."""

    def __init__(self, hass):
        """Initialize Rivian coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

        self._hass = hass



    async def _get_data(self) -> dict[str, Any]:
        rivian = Rivian()
        _LOGGER.info("====== _get_data ========")
        try:
            vi = await rivian.get_vehicle_info(self._hass, "##########") ## TODO: Take VIN as a param during config flow

            _LOGGER.info("====== VI ========")
            _LOGGER.info(vi["data"]["thermal/hvac_cabin_control/cabin_temperature"])
            return vi
        except Exception as ex:
            _LOGGER.info(ex)

    async def _async_update_data():
        _LOGGER.debug("============= Updating Rivian data ==============")
        # data = await self._hass.async_add_executor_job(self._get_data)
        # return data
        return {}

    def _validate(self) -> None:
        """Authenticate using Rivian API."""

    async def async_validate_input(self) -> None:
        """Get new sensor data for Rivian component."""
        await self.hass.async_add_executor_job(self._validate)

class RivianEntity(CoordinatorEntity):
    """Defines a base Rivian entity."""

    coordinator: RivianCoordinator

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Rivian device."""
        return DeviceInfo(
            identifiers={
                (DOMAIN)
            },
            name=f"Rivian - {self.coordinator.data[CONF_NAME_KEY]}",
            manufacturer="Rivian",

        )
