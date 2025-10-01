"""Vestaboard entity."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import VestaboardCoordinator

_LOGGER = logging.getLogger(__name__)


class VestaboardEntity(CoordinatorEntity[VestaboardCoordinator]):
    """Base class for Vestaboard entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: VestaboardCoordinator,
        entry: ConfigEntry,
        description: EntityDescription,
    ) -> None:
        """Construct a Vestaboard entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}-{description.key}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Vestaboard",
            model="Vestaboard",
        )
