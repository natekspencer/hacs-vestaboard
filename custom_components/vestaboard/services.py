"""Support for Vestaboard services."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv

from .const import (
    ALIGN_CENTER,
    ALIGNS,
    CONF_ALIGN,
    CONF_DECORATOR,
    CONF_MESSAGE,
    CONF_VALIGN,
    DECORATORS,
    DOMAIN,
    SERVICE_MESSAGE,
    VALIGN_MIDDLE,
    VALIGNS,
)
from .helpers import async_get_coordinator_by_device_id, construct_message

SERVICE_MESSAGE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
        vol.Required(CONF_MESSAGE): cv.string,
        vol.Optional(CONF_DECORATOR): vol.In(DECORATORS),
        vol.Optional(CONF_ALIGN, default=ALIGN_CENTER): vol.In(ALIGNS),
        vol.Optional(CONF_VALIGN, default=VALIGN_MIDDLE): vol.In(VALIGNS),
    }
)


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the Vestaboard integration."""

    async def _async_service_message(call: ServiceCall) -> None:
        """Send a message to a Vestaboard."""
        rows = construct_message(**{CONF_MESSAGE: ""} | call.data)
        for device_id in call.data[CONF_DEVICE_ID]:
            coordinator = async_get_coordinator_by_device_id(hass, device_id)
            if not coordinator.quiet_hours():
                coordinator.vestaboard.write_message(rows)

    hass.services.async_register(
        DOMAIN,
        SERVICE_MESSAGE,
        _async_service_message,
        schema=SERVICE_MESSAGE_SCHEMA,
    )
