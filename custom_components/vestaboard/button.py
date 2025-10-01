"""Vestaboard button entity."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import now as dt_now

from .const import DOMAIN
from .coordinator import VestaboardCoordinator
from .entity import VestaboardEntity

CLEAR_ALERT = ButtonEntityDescription(
    key="clear_alert",
    translation_key="clear_alert",
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Vestaboard binary sensors using config entry."""
    coordinator: VestaboardCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VestaboardButtonEntity(coordinator, entry, CLEAR_ALERT)])


class VestaboardButtonEntity(VestaboardEntity, ButtonEntity):
    """Vestaboard button entity."""

    async def async_press(self) -> None:
        """Press the button."""
        if (alert := self.coordinator.alert_expiration) and alert > (now := dt_now()):
            self.coordinator.alert_expiration = now
            await self.async_update()
