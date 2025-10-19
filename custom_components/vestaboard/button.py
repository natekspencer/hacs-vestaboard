"""Vestaboard button entity."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import now as dt_now

from .entity import VestaboardConfigEntry, VestaboardEntity

CLEAR_TEMPORARY_MESSAGE = ButtonEntityDescription(
    key="clear_temporary_message", translation_key="clear_temporary_message"
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VestaboardConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Vestaboard binary sensors using config entry."""
    async_add_entities([VestaboardButtonEntity(entry, CLEAR_TEMPORARY_MESSAGE)])


class VestaboardButtonEntity(VestaboardEntity, ButtonEntity):
    """Vestaboard button entity."""

    async def async_press(self) -> None:
        """Press the button."""
        expiration = self.coordinator.temporary_message_expiration
        if expiration and expiration > (now := dt_now()):
            await self.coordinator._handle_temporary_message_expiration(now)
