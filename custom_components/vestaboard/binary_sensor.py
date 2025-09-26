"""Vestaboard binary sensor entity."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.dt as dt_util

from .const import DOMAIN
from .coordinator import VestaboardCoordinator
from .entity import VestaboardEntity

ALERT_MESSAGE_ACTIVE = BinarySensorEntityDescription(
    key="alert_message_active",
    name="Alert Message Active",
    device_class=BinarySensorDeviceClass.RUNNING,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Vestaboard binary sensors using config entry."""
    coordinator: VestaboardCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VestaboardAlertActiveEntity(coordinator, entry, ALERT_MESSAGE_ACTIVE)])


class VestaboardAlertActiveEntity(VestaboardEntity, BinarySensorEntity):
    """Vestaboard alert active binary sensor entity."""

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return (
            self.coordinator.alert_expiration is not None
            and self.coordinator.alert_expiration > dt_util.now()
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs: dict[str, Any] = {}
        if exp_time := self.coordinator.alert_expiration:
            attrs["expiration_time"] = exp_time.isoformat()
        return attrs
