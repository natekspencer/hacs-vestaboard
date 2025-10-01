"""Support for Vestaboard services."""

from __future__ import annotations

from datetime import timedelta

import voluptuous as vol

from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import HomeAssistant, HomeAssistantError, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.httpx_client import get_async_client
import homeassistant.util.dt as dt_util

from .const import (
    ALIGN_CENTER,
    ALIGNS,
    CONF_ALIGN,
    CONF_DURATION,
    CONF_MESSAGE,
    CONF_VALIGN,
    CONF_VBML,
    DOMAIN,
    SERVICE_MESSAGE,
    VALIGN_MIDDLE,
    VALIGNS,
    VBML_URL,
)
from .helpers import (
    async_get_coordinator_by_device_id,
    construct_message,
    create_svg,
    decode,
)

_character_codes = vol.All(vol.Coerce(int), vol.Range(min=0, max=71))
_raw_characters = vol.All(cv.ensure_list, [vol.All(cv.ensure_list, [_character_codes])])
_style = vol.Schema(
    {
        vol.Optional("height"): vol.All(vol.Coerce(int), vol.Range(min=1, max=6)),
        vol.Optional("width"): vol.All(vol.Coerce(int), vol.Range(min=1, max=22)),
        vol.Optional("justify"): vol.In(["left", "right", "center", "justified"]),
        vol.Optional("align"): vol.In(["top", "bottom", "center", "justified"]),
        vol.Optional("absolutePosition"): vol.Schema(
            {
                vol.Required("x"): vol.All(vol.Coerce(int), vol.Range(min=0, max=21)),
                vol.Required("y"): vol.All(vol.Coerce(int), vol.Range(min=0, max=5)),
            }
        ),
    }
)
_component = vol.All(
    vol.Schema(
        {
            vol.Optional("template"): cv.string,
            vol.Optional("rawCharacters"): _raw_characters,
            vol.Optional("style"): _style,
        }
    ),
    cv.has_at_least_one_key("template", "rawCharacters"),
)

VBML_SCHEMA = vol.Schema(
    {
        vol.Optional("props"): {cv.string: cv.string},
        vol.Required("components"): vol.All(cv.ensure_list, [_component]),
    }
)

SERVICE_MESSAGE_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Required(CONF_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
            vol.Optional(CONF_MESSAGE): cv.string,
            vol.Optional(CONF_DURATION): vol.All(
                vol.Coerce(int), vol.Range(min=10, max=7200)
            ),
            vol.Optional(CONF_ALIGN, default=ALIGN_CENTER): vol.In(ALIGNS),
            vol.Optional(CONF_VALIGN, default=VALIGN_MIDDLE): vol.In(VALIGNS),
            vol.Optional(CONF_VBML): VBML_SCHEMA,
        },
    ),
    cv.has_at_least_one_key(CONF_MESSAGE, CONF_VBML),
)


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the Vestaboard integration."""

    async def _async_service_message(call: ServiceCall) -> None:
        """Send a message to a Vestaboard."""
        if vbml := call.data.get(CONF_VBML):
            client = get_async_client(hass)
            response = await client.post(VBML_URL, json=vbml)
            if response.is_error and b"message" in response.content:
                raise HomeAssistantError(response.json())
            response.raise_for_status()
            rows = response.json()
        else:
            rows = construct_message(**{CONF_MESSAGE: ""} | call.data)

        duration = call.data.get(CONF_DURATION)

        for device_id in call.data[CONF_DEVICE_ID]:
            coordinator = async_get_coordinator_by_device_id(hass, device_id)
            if coordinator.quiet_hours():
                continue

            async def write_and_update_state(message_rows: list[list[int]]):
                """Write to board and immediately update coordinator."""
                await hass.async_add_executor_job(
                    coordinator.vestaboard.write_message, message_rows
                )
                # Manually update coordinator state for instant UI feedback
                coordinator.message = decode(message_rows)
                coordinator.svg = create_svg(
                    message_rows, coordinator.model
                ).encode()
                coordinator.last_updated = dt_util.now()
                coordinator.async_set_updated_data(message_rows)

            if duration:  # This is an alert
                coordinator.alert_expiration = dt_util.now() + timedelta(
                    seconds=duration
                )
                await write_and_update_state(rows)
            else:  # This is a persistent message
                coordinator.persistent_message_rows = rows
                if not (
                    coordinator.alert_expiration
                    and coordinator.alert_expiration > dt_util.now()
                ):
                    await write_and_update_state(rows)

    hass.services.async_register(
        DOMAIN,
        SERVICE_MESSAGE,
        _async_service_message,
        schema=SERVICE_MESSAGE_SCHEMA,
    )
