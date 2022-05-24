"""The Rivian (Unofficial) integration."""
from __future__ import annotations

from datetime import timedelta
import logging

import async_timeout


from ...helpers.entity import DeviceInfo

from homeassistant.components.light import LightEntity
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from . import RivianCoordinator, RivianEntity
from .const import (
    DOMAIN,
    _LOGGER,
    CONF_THERMAL_HVAC_CABIN_CONTROL_CABIN_TEMPERATURE
)

UPDATE_INTERVAL=30
CONF_DATA_KEY = "config_data"

class RivianSensorEntityDescription(SensorEntityDescription):
    """Describes Rivian sensor entity."""
    precision: int | None = None


SENSOR_TYPES: dict[str, RivianSensorEntityDescription] = {
    CONF_THERMAL_HVAC_CABIN_CONTROL_CABIN_TEMPERATURE: RivianSensorEntityDescription(
        key=CONF_THERMAL_HVAC_CABIN_CONTROL_CABIN_TEMPERATURE,
        name="Cabin Temperature",
        # key="thermal/hvac_cabin_control/cabin_temperature",
    ),
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create Rivian sensor entities in HA."""
    coordinator: RivianCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            RivianSensor(coordinator, entry, description)
            for ent in coordinator.data
            if (description := SENSOR_TYPES.get(ent))
        ]
    )

class RivianSensor(RivianEntity, SensorEntity):
    """Rivian Sensor"""
    entity_description: RivianSensorEntityDescription
    coordinator: RivianCoordinator

    def __init__(
        self,
        coordinator: RivianCoordinator,
        entry: ConfigEntry,
        description: RivianSensorEntityDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"{entry.title} {description.name}"
        self._attr_unique_id = f"{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if (sensor_round := self.entity_description.precision) is not None:
            try:
                return cast(
                    StateType,
                    round(
                        self.coordinator.data[self.entity_description.key], sensor_round
                    ),
                )
            except TypeError:
                _LOGGER.debug("Cannot format %s", self._attr_name)
                return None
        return cast(StateType, self.coordinator.data[self.entity_description.key])
