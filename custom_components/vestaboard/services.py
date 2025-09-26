"""Support for Vestaboard services."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import HomeAssistant, HomeAssistantError, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.httpx_client import get_async_client

from .const import (
    ALIGN_CENTER,
    ALIGNS,
    CONF_ALIGN,
    CONF_DECORATOR,
    CONF_JUSTIFY,
    CONF_MESSAGE,
    CONF_VALIGN,
    CONF_VBML,
    DECORATOR_MUSIC,
    DECORATORS,
    DOMAIN,
    SERVICE_MESSAGE,
    VALIGN_MIDDLE,
    VALIGNS,
    VBML_URL,
)
from .helpers import MUSIC_HEADER, async_get_coordinator_by_device_id, construct_message

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
            vol.Optional(CONF_DECORATOR): vol.In(DECORATORS),
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

        async def _translate_vbml(vbml: dict) -> list[list[int]]:
            """Translate VBML."""
            client = get_async_client(hass)
            response = await client.post(VBML_URL, json=vbml)
            if response.is_error and b"message" in response.content:
                raise HomeAssistantError(response.json())
            response.raise_for_status()
            return response.json()

        if vbml := call.data.get(CONF_VBML):
            rows = await _translate_vbml(vbml)
        else:
            try:
                rows = construct_message(**{CONF_MESSAGE: ""} | call.data)
            except ValueError:
                align = call.data.get(CONF_VALIGN, ALIGN_CENTER).replace(
                    VALIGN_MIDDLE, ALIGN_CENTER
                )
                justify = call.data.get(CONF_ALIGN, ALIGN_CENTER)
                message = {
                    "style": {CONF_ALIGN: align, CONF_JUSTIFY: justify},
                    "template": call.data.get(CONF_MESSAGE, ""),
                }
                components = [message]

                if call.data.get(CONF_DECORATOR, "") == DECORATOR_MUSIC:
                    message["style"]["height"] = 5
                    now_playing = {
                        "style": {"height": 1},
                        "template": "".join(f"{{{n}}}" for n in MUSIC_HEADER),
                    }
                    components.insert(0, now_playing)

                vbml = {"components": components}
                rows = await _translate_vbml(vbml)

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
