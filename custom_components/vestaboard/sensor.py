"""Vestaboard sensor entity."""
from __future__ import annotations

from datetime import datetime

import homeassistant.util.dt as dt_util

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import VestaboardCoordinator
from .entity import VestaboardEntity

MESSAGE = SensorEntityDescription(key="message", name="Message")

ALERT_EXPIRATION = SensorEntityDescription(
    key="alert_expiration",
    name="Alert Expiration",
    device_class=SensorDeviceClass.TIMESTAMP,
    entity_category=EntityCategory.DIAGNOSTIC,
)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Vestaboard sensors using config entry."""
    coordinator: VestaboardCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            VestaboardSensorEntity(coordinator, entry, MESSAGE),
            VestaboardAlertExpirationSensorEntity(
                coordinator, entry, ALERT_EXPIRATION
            ),
        ]
    )


class VestaboardSensorEntity(VestaboardEntity, SensorEntity):
    """Vestaboard sensor entity."""

    @property
    def native_value(self) -> str | None:
        """Return the value reported by the sensor."""
        return self.coordinator.message

class VestaboardAlertExpirationSensorEntity(VestaboardEntity, SensorEntity):
    """Vestaboard alert expiration sensor entity."""

    @property
    def native_value(self) -> datetime | None:
        """Return the value reported by the sensor."""
        if (
            self.coordinator.alert_expiration is not None
            and self.coordinator.alert_expiration > dt_util.now()
        ):
            return self.coordinator.alert_expiration
        return None
