"""Support for Vestaboard."""
from __future__ import annotations

import logging

from homeassistant.components import notify as hass_notify
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import discovery
from homeassistant.helpers.typing import ConfigType

from .const import DATA_HASS_CONFIG, DOMAIN
from .coordinator import VestaboardCoordinator
from .helpers import create_client
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.IMAGE,
    Platform.SENSOR,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Vestaboard integration."""
    async_setup_services(hass)
    hass.data[DOMAIN] = {DATA_HASS_CONFIG: config}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vestaboard from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    client = create_client(entry.data)
    coordinator = VestaboardCoordinator(hass, client, entry.options)
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.data:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Set up notify platform, no entry support for notify component yet,
    # have to use discovery to load platform.
    hass.async_create_task(
        discovery.async_load_platform(
            hass,
            Platform.NOTIFY,
            DOMAIN,
            {CONF_NAME: entry.title, "entry_id": entry.entry_id},
            hass.data[DOMAIN][DATA_HASS_CONFIG],
        )
    )
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        del hass.data[DOMAIN][entry.entry_id]
        await hass_notify.async_reload(hass, DOMAIN)
    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
