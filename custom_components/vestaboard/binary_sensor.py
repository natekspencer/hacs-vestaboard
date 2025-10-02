"""Vestaboard binary sensor entity."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
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
    async_add_entities(
        [VestaboardBinarySensorEntity(coordinator, entry, TEMPORARY_MESSAGE)]
    )


TEMPORARY_MESSAGE = BinarySensorEntityDescription(
    key="temporary_message",
    translation_key="temporary_message",
    entity_category=EntityCategory.DIAGNOSTIC,
)


class VestaboardBinarySensorEntity(VestaboardEntity, BinarySensorEntity):
    """Vestaboard binary sensor entity."""

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        expiration = self.coordinator.temporary_message_expiration
        return expiration is not None and expiration > dt_now()
