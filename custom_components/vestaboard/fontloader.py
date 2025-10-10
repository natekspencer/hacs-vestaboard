"""Fontloader."""

from __future__ import annotations

from importlib import resources
import io
from typing import Final

from PIL import ImageFont

FONT_NAME: Final = "Vestaboard.otf"


def _load_font_bytes() -> bytes:
    """Load the raw font bytes from the font file."""
    return resources.read_binary(__package__, FONT_NAME)


def get_font_buffer() -> io.BytesIO:
    """Return the font as a BytesIO stream."""
    return io.BytesIO(_load_font_bytes())


def get_font_bytes() -> bytes:
    """Return raw font bytes."""
    return _load_font_bytes()


def load_font(size: float | None) -> ImageFont:
    """Load a font."""
    try:
        return ImageFont.truetype(get_font_buffer(), size=size)
    except OSError:
        return ImageFont.load_default(size)
