"""Vestaboard model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Final, Self

DEFAULT_COLOR_MAP: Final[dict[int, str]] = {
    0: "#141414",  # blank
    63: "#DA291C",  # red
    64: "#FA7400",  # orange
    65: "#FCB81B",  # yellow
    66: "#1F9A44",  # green
    67: "#2083D5",  # blue
    68: "#702F8A",  # violet
    69: "#FFFFFF",  # white
    70: "#141414",  # black
    71: "#FFFFFF",  # filled
}


@dataclass(frozen=True, slots=True)
class VestaboardModel:
    """Encapsulates Vestaboard model specifics, colors, chars, layout, and board styling."""

    name: str

    _MODELS: ClassVar[dict[str, dict]] = {
        "black": {
            "frame": "#171818",
            "bit": "#333333",
            "text": "#FFFFFF",
            "rows": 6,
            "columns": 22,
            "aspect_ratio": 1.87,
            "color_map": DEFAULT_COLOR_MAP,
            "char_map": {62: "°"},
        },
        "white": {
            "frame": "#F5F5F7",
            "bit": "#CCCCCC",
            "text": "#000000",
            "rows": 6,
            "columns": 22,
            "aspect_ratio": 1.87,
            "color_map": DEFAULT_COLOR_MAP
            | {
                0: "#FFFFFF",
                69: "#000000",
                70: "#FFFFFF",
                71: "#000000",
            },
            "char_map": {62: "°"},
        },
        "note": {
            "frame": "#171818",
            "bit": "#333333",
            "text": "#FFFFFF",
            "rows": 3,
            "columns": 15,
            "aspect_ratio": 2.35,
            "color_map": DEFAULT_COLOR_MAP,
            "char_map": {62: "❤️"},
        },
    }

    @property
    def bit_color(self) -> str:
        """Return the bit color."""
        return self._MODELS[self.name]["bit"]

    @property
    def frame_color(self) -> str:
        """Return the frame color."""
        return self._MODELS[self.name]["frame"]

    @property
    def text_color(self) -> str:
        """Return the text color."""
        return self._MODELS[self.name]["text"]

    @property
    def color_map(self) -> dict[int, str]:
        """Return the color map."""
        return self._MODELS[self.name]["color_map"]

    @property
    def char_map(self) -> dict[int, str]:
        """Return the character map."""
        return self._MODELS[self.name]["char_map"]

    @property
    def rows(self) -> int:
        """Return the number of rows."""
        return self._MODELS[self.name]["rows"]

    @property
    def columns(self) -> int:
        """Return the number of columns."""
        return self._MODELS[self.name]["columns"]

    @property
    def aspect_ratio(self) -> float:
        """Return the aspect ratio."""
        return self._MODELS[self.name]["aspect_ratio"]

    def color_for_code(self, code: int) -> str | None:
        """Return the hex color for a numeric color code, if defined."""
        return self.color_map.get(code)

    def char_for_code(self, code: int) -> str | None:
        """Return the character override for a given code, if defined."""
        return self.char_map.get(code)

    def is_flagship(self) -> bool:
        """Return True for the flagship models (black or white)."""
        return self.name in ("black", "white")

    def tile_size(
        self, target_width: float, target_height: float
    ) -> tuple[float, float]:
        """Calculate the tile size."""
        tile_width = target_width / self.columns
        tile_height = target_height / self.rows
        return tile_width, tile_height

    def tile_aspect_ratio(self, target_width: float, target_height: float) -> float:
        """Calculate the tile aspect ratio."""
        tile_width, tile_height = self.tile_size(target_width, target_height)
        return tile_width / tile_height

    @classmethod
    def all_models(cls) -> list[str]:
        """Return all known Vestaboard model names."""
        return list(cls._MODELS.keys())

    @classmethod
    def from_name(cls, name: str) -> Self:
        """Factory with validation."""
        if name not in cls._MODELS:
            raise ValueError(f"Unknown Vestaboard model: {name!r}")
        return cls(name)
