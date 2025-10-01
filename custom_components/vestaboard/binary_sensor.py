"""Vestaboard binary sensor entity."""
from __future__ import annotations

from typing import Any

import homeassistant.util.dt as dt_util

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback


from .const import DOMAIN
from .coordinator import VestaboardCoordinator
from .entity import VestaboardEntity

ALERT_ACTIVE = BinarySensorEntityDescription(
    key="alert_active",
    name="Alert Active",
    device_class=BinarySensorDeviceClass.RUNNING,
    entity_category=EntityCategory.DIAGNOSTIC,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Vestaboard binary sensors using config entry."""
    coordinator: VestaboardCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VestaboardAlertActiveEntity(coordinator, entry, ALERT_ACTIVE)])


class VestaboardAlertActiveEntity(VestaboardEntity, BinarySensorEntity):
    """Vestaboard alert active binary sensor entity."""

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return (
            self.coordinator.alert_expiration is not None
            and self.coordinator.alert_expiration > dt_util.now()
        )
