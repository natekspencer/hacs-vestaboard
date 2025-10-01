"""Vestaboard binary sensor entity."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import now as dt_now

from .const import DOMAIN
from .coordinator import VestaboardCoordinator
from .entity import VestaboardEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Vestaboard binary sensors using config entry."""
    coordinator: VestaboardCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VestaboardBinarySensorEntity(coordinator, entry, ALERT)])


ALERT = BinarySensorEntityDescription(
    key="alert",
    translation_key="alert",
    device_class=BinarySensorDeviceClass.RUNNING,
    entity_category=EntityCategory.DIAGNOSTIC,
)


class VestaboardBinarySensorEntity(VestaboardEntity, BinarySensorEntity):
    """Vestaboard binary sensor entity."""

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return (alert := self.coordinator.alert_expiration) and alert > dt_now()
