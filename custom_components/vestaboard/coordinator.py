"""Vestaboard coordinator."""
from __future__ import annotations

from datetime import timedelta
import logging

import async_timeout
from vesta import LocalClient

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, MODEL_BLACK
from .helpers import create_svg, decode

_LOGGER = logging.getLogger(__name__)


class VestaboardCoordinator(DataUpdateCoordinator):
    """Vestaboard data update coordinator."""

    data: list[list[int]] | None
    message: str | None
    svg: bytes | None

    def __init__(
        self, hass: HomeAssistant, vestaboard: LocalClient, model: str = MODEL_BLACK
    ) -> None:
        """Initialize."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=15)
        )
        self.vestaboard = vestaboard
        self.model = model

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                data = self.vestaboard.read_message()
        except Exception as ex:
            raise UpdateFailed("Couldn't read vestaboard") from ex
        if data is None:
            raise ConfigEntryAuthFailed
        if data != self.data:
            self.message = decode(data)
            self.svg = create_svg(data, self.model).encode()
        return data
