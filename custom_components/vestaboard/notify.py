"""Support for Vestaboard notifications."""
from __future__ import annotations

from typing import Any

from vesta import LocalClient

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
    return VestaboardNotificationService(coordinator.vestaboard)


class VestaboardNotificationService(BaseNotificationService):
    """Implement the notification service for Vestaboard."""

    def __init__(self, vestaboard: LocalClient) -> None:
        """Initialize the service."""
        self.vestaboard = vestaboard

    def send_message(self, message: str = "", **kwargs: Any) -> None:
        """Send a message to a Vestaboard."""
        if not (data := kwargs.get(ATTR_DATA)):
            data = {}
        self.vestaboard.write_message(construct_message(message, **data))
