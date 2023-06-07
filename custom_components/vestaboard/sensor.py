"""Vestaboard sensor entity."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import VestaboardCoordinator
from .entity import VestaboardEntity

MESSAGE = SensorEntityDescription(key="message", name="Message")


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Vestaboard sensors using config entry."""
    coordinator: VestaboardCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VestaboardSensorEntity(coordinator, entry, MESSAGE)])


class VestaboardSensorEntity(VestaboardEntity, SensorEntity):
    """Vestaboard sensor entity."""

    @property
    def native_value(self) -> str | None:
        """Return the value reported by the sensor."""
        return self.coordinator.message
