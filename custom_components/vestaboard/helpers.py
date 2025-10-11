"""Helpers for the Vestaboard integration."""

from __future__ import annotations

import base64
import io
from typing import TYPE_CHECKING, Any, cast

import httpx
from PIL import Image, ImageDraw
from vesta import Color, LocalClient, encode_text

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.util.ssl import get_default_context

from .const import (
    ALIGN_CENTER,
    ALIGN_JUSTIFIED,
    CONF_ALIGN,
    CONF_ENABLEMENT_TOKEN,
    CONF_JUSTIFY,
    DOMAIN,
    MODEL_BLACK,
)
from .fontloader import get_font_bytes, load_font
from .vestaboard_model import VestaboardModel

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
    "❤️": "{62}",
}


def construct_message(message: str, **kwargs: Any) -> list[list[int]]:
    """Construct a message."""
    message = "".join(EMOJI_MAP.get(char, char) for char in message)
    align = kwargs.get(CONF_JUSTIFY, ALIGN_CENTER)
    if align in (ALIGN_JUSTIFIED):
        align = ALIGN_CENTER
    valign = kwargs.get(CONF_ALIGN, ALIGN_CENTER)
    if valign in (ALIGN_CENTER, ALIGN_JUSTIFIED):
        valign = "middle"
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


def create_png(
    data: list[list[int]], color: str = MODEL_BLACK, height: int = 1080
) -> bytes:
    model = VestaboardModel.from_name(color)

    width = int(height * model.aspect_ratio)
    n_cols = model.columns

    # Derive scale from target height to preserve original proportions
    scale = height / 1.77

    # Tile sizes
    tile_w = scale * 0.09
    tile_h = scale * 0.11

    # Padding / start
    start = 0.2

    # Column spacing to fit first/last column exactly
    column_multiplier = ((width - start * scale * 2) - n_cols * tile_w) / (n_cols - 1)

    # Row multiplier same as original
    row_multiplier = 0.24

    # Create image
    img = Image.new("RGB", (width, height), color=model.frame_color)
    draw = ImageDraw.Draw(img)

    # Board background
    draw.rectangle(
        [(0, 0), (width, height)],
        outline=model.bit_color,
        width=int(scale * 0.02),
    )

    # Font
    font = load_font(int(tile_h * 1.1))

    # Draw tiles and characters
    for row, characters in enumerate(data):
        for column, code in enumerate(characters):
            xpos = start * scale + column * column_multiplier + tile_w * column
            ypos = start * scale + row * row_multiplier * scale

            if code in (c.value for c in Color):
                draw.rectangle(
                    [(xpos, ypos), (xpos + tile_w, ypos + tile_h * 0.84)],
                    fill=model.color_map[code],
                )
                offset = 0.001 * scale * 0.84
                draw.rectangle(
                    [
                        (xpos, ypos + tile_h * 0.84 / 2 - offset),
                        (xpos + tile_w, ypos + tile_h * 0.84 / 2 + offset),
                    ],
                    fill=model.frame_color,
                )
            else:
                char = symbol(code)

                cx = xpos + tile_w / 2
                cy = ypos + tile_h / 2
                draw.text((cx, cy), char, fill=model.text_color, font=font, anchor="mm")

    # Logo text
    logo_font = load_font(int(0.048 * scale))
    draw.text(
        (width / 2, scale * 1.64),
        "VESTABOARD",
        fill=model.bit_color,
        anchor="mm",
        font=logo_font,
    )

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def create_svg(data: list[list[int]], color: str = MODEL_BLACK) -> str:
    """Create an svg for the message from the Vestaboard."""
    model = VestaboardModel(color)

    encoded_font = base64.b64encode(get_font_bytes()).decode("ascii")
    font_face = f"""@font-face {{
        font-family: "Vestaboard";
        src: url("data:font/otf;base64,{encoded_font}") format("opentype");
      }}"""

    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4 1.77" version="1.1">'
    svg += f"<style> {font_face} </style>"
    svg += '<style> svg { font-family: "Vestaboard", "Regular", sans-serif; text-anchor: middle; }'
    svg += f".board {{ fill: {model.frame_color}; stroke: {model.bit_color}; stroke-width: 0.02; }}"
    svg += f".char {{ font-size: 0.14px; width: 0.09px; height: 0.11px; }} text.char {{ fill: {model.text_color}; transform: translateY(0.105px); }}"
    svg += " ".join(
        f".{Color(k).name.lower()} {{ fill: {v}; }}" for k, v in model.color_map.items()
    )
    svg += f".logo {{ font-size: 0.10px; fill: {model.bit_color}; }} </style>"
    svg += '<rect class="board" x="0.01" y="0.01" width="3.98" height="1.75" />'
    start = 0.2
    row_multiplier = 0.24
    column_multiplier = 0.166
    for row, characters in enumerate(data):
        for column, code in enumerate(characters):
            xpos = round(start + column * column_multiplier, 3)
            ypos = round(start + row * row_multiplier, 3)
            if code in (c.value for c in Color):
                svg += f'<rect class="char {Color(code).name.lower()}" x="{xpos}" y="{ypos}"/>'
            else:
                svg += f'<text class="char" x="{xpos + 0.045}" y="{ypos}">{symbol(code).replace("&", "&amp;")}</text>'
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
