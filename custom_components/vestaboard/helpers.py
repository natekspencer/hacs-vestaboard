"""Helpers for the Vestaboard integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import httpx
from vesta import Color, LocalClient, encode_row, encode_text

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.util.ssl import get_default_context

from .const import (
    ALIGN_CENTER,
    CONF_ALIGN,
    CONF_ENABLEMENT_TOKEN,
    CONF_VALIGN,
    DECORATOR_MUSIC,
    DOMAIN,
    MODEL_BLACK,
    VALIGN_MIDDLE,
)

if TYPE_CHECKING:
    from .coordinator import VestaboardCoordinator

PRINTABLE = (
    " ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$() - +&=;: '\"%,.  /? °🟥🟧🟨🟩🟦🟪⬜⬛■"
)
EMOJI_MAP = {
    "🟥": "{63}",
    "🟧": "{64}",
    "🟨": "{65}",
    "🟩": "{66}",
    "🟦": "{67}",
    "🟪": "{68}",
    "⬜": "{69}",
    "⬛": "{70}",
    "■": "{71}",
}

def construct_message(message: str, **kwargs: Any) -> list[list[int]]:
    """Construct a message."""
    message = "".join(EMOJI_MAP.get(char, char) for char in message)
    align = kwargs.get(CONF_ALIGN, ALIGN_CENTER)
    valign = kwargs.get(CONF_VALIGN, VALIGN_MIDDLE)
    return encode_text(message, align=align, valign=valign)

def create_client(data: dict[str, Any]) -> LocalClient:
    """Create a Vestaboard local client."""
    url = f"http://{data['host']}:7000"
    key = data["api_key"]
    http_client = httpx.Client(verify=get_default_context())
    if data.get(CONF_ENABLEMENT_TOKEN):
        client = LocalClient(base_url=url, http_client=http_client)
        client.enable(key)
        return client
    return LocalClient(local_api_key=key, base_url=url, http_client=http_client)


def create_svg(data: list[list[int]], color: str = MODEL_BLACK) -> str:
    """Create an svg for the message from the Vestaboard."""
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4 1.77" version="1.1" class="{color}">'
    svg += '<style> svg { font-family: "HelveticaNeue", "Roboto", sans-serif; text-anchor: middle; } .black>.board { fill: #171818; stroke: #333333; } .white>.board { fill: #F5F5F7; stroke: #CCCCCC; } .board { stroke-width: 0.02; } .char { font-size: 0.14px; width: 0.09px; height: 0.11px; } text.char { transform: translateY(0.105px); } .black, .white>text.char, .black>rect.blank { fill: #141414; } .white, .black>text.char, .white>rect.blank { fill: #FFFFFF; } .red { fill: #DA291C; } .orange { fill: #FA7400; } .yellow { fill: #FCB81B; } .green { fill: #1F9A44; } .blue { fill: #2083D5; } .violet { fill: #702F8A; } .logo { font-size: 0.11px; } .black>.logo { fill: #333333; } .white>.logo { fill: #CCCCCC; } </style>'
    svg += '<rect class="board" x="0.01" y="0.01" width="3.98" height="1.75" />'
    start = 0.2
    row_multiplier = 0.24
    column_multiplier = 0.166
    for row, characters in enumerate(data):
        for column, code in enumerate(characters):
            xpos = start + column * column_multiplier
            ypos = start + row * row_multiplier
            if code in (c.value for c in Color):
                svg += f'<rect class="char {Color(code).name.lower()}" x="{xpos}" y="{ypos}"/>'
            else:
                svg += f'<text class="char" x="{xpos+0.045}" y="{ypos}">{symbol(code).replace("&","&amp;")}</text>'
    svg += '<text class="logo" x="50%" y="1.68">VESTABOARD</text></svg>'
    return svg


def decode(data: list[int] | list[list[int]]) -> None:
    """Prints a console-formatted representation of encoded character data.

    ``data`` may be a single list or a two-dimensional array of character codes.
    """
    rows = cast(list[list[int]], data if data and isinstance(data[0], list) else [data])
    return "\n".join((f"{''.join(map(symbol, row))}" for row in rows))


def symbol(code: int) -> str:
    """Convert a character code to symbol."""
    return PRINTABLE[code] if 0 <= code < len(PRINTABLE) else " "


@callback
def async_get_coordinator_by_device_id(
    hass: HomeAssistant, device_id: str
) -> VestaboardCoordinator:
    """Get the Vestaboard coordinator for this device ID."""
    device_registry = dr.async_get(hass)

    if (device_entry := device_registry.async_get(device_id)) is None:
        raise ValueError(f"Unknown Vestaboard device ID: {device_id}")

    for entry_id in device_entry.config_entries:
        if (
            (entry := hass.config_entries.async_get_entry(entry_id))
            and entry.domain == DOMAIN
            and entry.entry_id in hass.data[DOMAIN]
        ):
            coordinator: VestaboardCoordinator = hass.data[DOMAIN][entry.entry_id]
            return coordinator

    raise ValueError(f"No coordinator for device ID: {device_id}")
