"""Vestaboard sensor entity."""
from __future__ import annotations

from homeassistant.components.camera import Camera, CameraEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import VestaboardCoordinator
from .entity import VestaboardEntity

CAMERA = CameraEntityDescription(key="board")


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Vestaboard camera using config entry."""
    coordinator: VestaboardCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VestaboardCamera(coordinator, entry, CAMERA)])


class VestaboardCamera(VestaboardEntity, Camera):
    """Vestaboard camera."""

    def __init__(
        self,
        coordinator: VestaboardCoordinator,
        entry_id: str,
        description: CameraEntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, entry_id, description)
        Camera.__init__(self)
        self.content_type = "image/svg+xml"

    def camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
        return self.coordinator.svg
