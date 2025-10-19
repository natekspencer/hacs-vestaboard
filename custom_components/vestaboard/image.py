"""Vestaboard image entity."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.image import ImageEntity, ImageEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import VestaboardConfigEntry
from .entity import VestaboardEntity

IMAGE = ImageEntityDescription(key="board", name=None)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VestaboardConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Vestaboard camera using config entry."""
    async_add_entities([VestaboardImageEntity(entry, IMAGE)])


class VestaboardImageEntity(VestaboardEntity, ImageEntity):
    """Vestaboard image entity."""

    _attr_content_type = "image/png"

    def __init__(
        self,
        entry: VestaboardConfigEntry,
        description: ImageEntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(entry, description)
        ImageEntity.__init__(self, entry.runtime_data.hass)

    @property
    def image_last_updated(self) -> datetime | None:
        """The time when the image was last updated."""
        return self.coordinator.last_updated

    def image(self) -> bytes | None:
        """Return bytes of image."""
        return self.coordinator.image
