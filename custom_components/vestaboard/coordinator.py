"""Vestaboard coordinator."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

import async_timeout
from vesta import LocalClient

from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

from .const import CONF_MODEL, CONF_QUIET_END, CONF_QUIET_START, DOMAIN, MODEL_BLACK
from .helpers import create_svg, decode

_LOGGER = logging.getLogger(__name__)


class VestaboardCoordinator(DataUpdateCoordinator):
    """Vestaboard data update coordinator."""

    data: list[list[int]] | None
    last_updated: datetime | None = None
    message: str | None
    svg: bytes | None
    persistent_message: list[list[int]] | None = None
    temporary_message_expiration: datetime | None = None
    _cancel_cb: CALLBACK_TYPE | None = None

    _read_errors: int = 0

    def __init__(
        self,
        hass: HomeAssistant,
        vestaboard: LocalClient,
        options: dict[str, Any],
    ) -> None:
        """Initialize."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=15)
        )
        self.vestaboard = vestaboard

        self.model = options.get(CONF_MODEL, MODEL_BLACK)
        if (start := options.get(CONF_QUIET_START)) != (
            end := options.get(CONF_QUIET_END)
        ):
            self.quiet_start = dt_util.parse_time(start)
            self.quiet_end = dt_util.parse_time(end)
        else:
            self.quiet_start = self.quiet_end = None

    def process_data(self, data: list[list[int]]) -> list[list[int]]:
        """Process data."""
        if data != self.data:
            self.last_updated = dt_util.now()
            self.message = decode(data)
            self.svg = create_svg(data, self.model).encode()
        return data

    def quiet_hours(self) -> bool:
        """Check if quiet hours."""
        if self.quiet_start and self.quiet_end:
            now = dt_util.now().time()
            if self.quiet_start < self.quiet_end:
                return self.quiet_start <= now < self.quiet_end
            return self.quiet_start <= now or now < self.quiet_end
        return False

    async def _async_update_data(self):
        """Fetch data from Vestaboard."""
        try:
            async with async_timeout.timeout(10):
                data = await self.hass.async_add_executor_job(
                    self.vestaboard.read_message
                )
        except Exception as ex:
            raise UpdateFailed(
                f"Couldn't read vestaboard at {self.vestaboard.http.base_url.host}"
            ) from ex
        if data is None:
            raise ConfigEntryAuthFailed

        if self.persistent_message is None:
            self.persistent_message = data

        return self.process_data(data)

    async def write_and_update_state(self, message_rows: list[list[int]]) -> None:
        """Write to board and immediately update coordinator."""
        await self.hass.async_add_executor_job(
            self.vestaboard.write_message, message_rows
        )
        # Manually update coordinator state for instant UI feedback
        self.async_set_updated_data(self.process_data(message_rows))

    async def _handle_temporary_message_expiration(self, now: datetime) -> None:
        """Handle temporary message expiration."""
        _LOGGER.debug(
            "Vestaboard temporary message expired @ %s, reverting to persistent message",
            now,
        )
        self.temporary_message_expiration = None
        if rows := self.persistent_message:
            await self.write_and_update_state(rows)
        if self._cancel_cb:
            self._cancel_cb()
            self._cancel_cb = None
