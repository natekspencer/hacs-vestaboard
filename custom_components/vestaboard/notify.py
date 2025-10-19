"""Support for Vestaboard notifications."""

from __future__ import annotations

from typing import Any

from homeassistant.components.notify import (
    ATTR_DATA,
    DOMAIN as NOTIFY_DOMAIN,
    BaseNotificationService,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
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
    return VestaboardNotificationService(discovery_info) if discovery_info else None


class VestaboardNotificationService(BaseNotificationService):
    """Implement the notification service for Vestaboard."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the service."""
        self.coordinator: VestaboardCoordinator = config["coordinator"]

    def send_message(self, message: str, **kwargs: Any) -> None:
        """Send a message to a Vestaboard."""
        ir.create_issue(
            self.hass,
            DOMAIN,
            f"deprecated_{NOTIFY_DOMAIN}_{DOMAIN}_{self._service_name}",
            is_fixable=False,
            issue_domain=DOMAIN,
            severity=ir.IssueSeverity.WARNING,
            translation_key=f"deprecated_{NOTIFY_DOMAIN}_{DOMAIN}",
            translation_placeholders={"action_name": self._service_name},
        )

        if self.coordinator.quiet_hours():
            return

        if not (data := kwargs.get(ATTR_DATA)):
            data = {}
        self.coordinator.vestaboard.write_message(construct_message(message, **data))
