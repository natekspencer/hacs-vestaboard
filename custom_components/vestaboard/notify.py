"""Support for Vestaboard notifications."""

from __future__ import annotations

from typing import Any


from homeassistant.components.notify import ATTR_DATA, BaseNotificationService
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN
from .coordinator import VestaboardCoordinator
from .helpers import construct_message


async def async_get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> VestaboardNotificationService | None:
    """Get the Vestaboard notification service."""
    if discovery_info is None:
        return None
    coordinator: VestaboardCoordinator = hass.data[DOMAIN][discovery_info["entry_id"]]
    return VestaboardNotificationService(coordinator)


class VestaboardNotificationService(BaseNotificationService):
    """Implement the notification service for Vestaboard."""

    def __init__(self, coordinator: VestaboardCoordinator) -> None:
        """Initialize the service."""
        self.coordinator = coordinator

    def send_message(self, message: str = "", **kwargs: Any) -> None:
        """Send a message to a Vestaboard."""
        if self.coordinator.quiet_hours():
            return

        if not (data := kwargs.get(ATTR_DATA)):
            data = {}
        self.coordinator.vestaboard.write_message(construct_message(message, **data))
