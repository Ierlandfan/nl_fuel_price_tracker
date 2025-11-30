"""Scheduled updates for Dutch Fuel Prices integration."""
from __future__ import annotations

import asyncio
from datetime import datetime, time, timedelta
import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_SCHEDULED_UPDATES,
    CONF_SCHEDULED_UPDATE_TIMES,
    DEFAULT_SCHEDULED_UPDATE_TIMES,
)

_LOGGER = logging.getLogger(__name__)


class ScheduledUpdates:
    """Handle scheduled price updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        update_callback,
    ) -> None:
        """Initialize scheduled updates."""
        self.hass = hass
        self.entry = entry
        self._update_callback = update_callback
        self._unsub_trackers = []

    async def async_setup(self) -> None:
        """Set up scheduled updates."""
        if not self.entry.data.get(CONF_SCHEDULED_UPDATES, False):
            _LOGGER.debug("Scheduled updates disabled")
            return

        update_times = self.entry.data.get(
            CONF_SCHEDULED_UPDATE_TIMES, DEFAULT_SCHEDULED_UPDATE_TIMES
        )

        if not update_times:
            _LOGGER.warning("No scheduled update times configured")
            return

        _LOGGER.info("Setting up scheduled updates at: %s", update_times)

        for time_str in update_times:
            try:
                # Parse time string (HH:MM:SS)
                hour, minute, second = map(int, time_str.split(":"))
                
                # Schedule update at this time
                unsub = async_track_time_change(
                    self.hass,
                    self._async_scheduled_update,
                    hour=hour,
                    minute=minute,
                    second=second,
                )
                self._unsub_trackers.append(unsub)
                
                _LOGGER.debug(
                    "Scheduled update at %02d:%02d:%02d",
                    hour, minute, second
                )
                
            except (ValueError, TypeError) as err:
                _LOGGER.error("Invalid time format '%s': %s", time_str, err)

    @callback
    async def _async_scheduled_update(self, now: datetime) -> None:
        """Execute scheduled update."""
        _LOGGER.info("Running scheduled fuel price update at %s", now.strftime("%H:%M:%S"))
        
        try:
            # Call the update callback
            await self._update_callback()
            _LOGGER.debug("Scheduled update completed successfully")
            
        except Exception as err:
            _LOGGER.error("Error during scheduled update: %s", err)

    async def async_unload(self) -> None:
        """Unload scheduled updates."""
        for unsub in self._unsub_trackers:
            unsub()
        self._unsub_trackers.clear()
        _LOGGER.debug("Scheduled updates unloaded")
