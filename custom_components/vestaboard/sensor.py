"""Vestaboard sensor entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Mapping

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import VestaboardCoordinator
from .entity import VestaboardEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Vestaboard sensors using config entry."""
    coordinator: VestaboardCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        VestaboardSensorEntity(coordinator, entry, description)
        for description in SENSORS
    )


@dataclass(kw_only=True)
class VestaboardSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[VestaboardCoordinator], datetime | str | None]


SENSORS = (
    VestaboardSensorEntityDescription(
        key="message",
        translation_key="message",
        value_fn=lambda coor: coor.message,
    ),
    VestaboardSensorEntityDescription(
        key="temporary_message_expiration",
        translation_key="temporary_message_expiration",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coor: coor.temporary_message_expiration,
    ),
)


class VestaboardSensorEntity(VestaboardEntity, SensorEntity):
    """Vestaboard sensor entity."""

    entity_description: VestaboardSensorEntityDescription

    @property
    def native_value(self) -> str | None:
        """Return the value reported by the sensor."""
        return self.entity_description.value_fn(self.coordinator)

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return entity specific state attributes."""
        if self.entity_description.key == "message" and (data := self.coordinator.data):
            character_codes = "".join(f"{{{code}}}" for row in data for code in row)
            return {"character_codes": character_codes}
        return None
