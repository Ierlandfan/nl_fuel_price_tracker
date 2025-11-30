"""Dutch Fuel Prices Integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
from .api import FuelPriceAPI
from .daily_notifications import DailyNotificationManager
from .scheduled_updates import ScheduledUpdates

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dutch Fuel Prices from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Initialize daily notification manager if not already done
    if "daily_manager" not in hass.data[DOMAIN]:
        daily_manager = DailyNotificationManager(hass)
        hass.data[DOMAIN]["daily_manager"] = daily_manager
    
    session = async_get_clientsession(hass)
    api = FuelPriceAPI(session)
    
    coordinator = FuelPriceCoordinator(hass, api, entry)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Set up daily notifications for this entry
    daily_manager = hass.data[DOMAIN]["daily_manager"]
    await daily_manager.setup(entry)
    
    # Set up scheduled updates
    scheduled_updates = ScheduledUpdates(
        hass,
        entry,
        coordinator.async_request_refresh
    )
    await scheduled_updates.async_setup()
    hass.data[DOMAIN][f"{entry.entry_id}_scheduled"] = scheduled_updates
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload scheduled updates
    if f"{entry.entry_id}_scheduled" in hass.data[DOMAIN]:
        scheduled_updates = hass.data[DOMAIN][f"{entry.entry_id}_scheduled"]
        await scheduled_updates.async_unload()
        hass.data[DOMAIN].pop(f"{entry.entry_id}_scheduled")
    
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class FuelPriceCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fuel price data updates."""

    def __init__(self, hass: HomeAssistant, api: FuelPriceAPI, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        update_interval = entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=update_interval),
        )
        self.api = api
        self.entry = entry

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            latitude = self.entry.data.get("latitude")
            longitude = self.entry.data.get("longitude")
            radius = self.entry.data.get("radius", 10)
            fuel_type = self.entry.data.get("fuel_type", "euro95")
            
            stations = await self.api.get_fuel_prices(
                latitude, longitude, radius, fuel_type
            )
            
            if not stations:
                _LOGGER.warning("No fuel stations found in radius")
                return {}
            
            # Find cheapest station
            cheapest = min(stations, key=lambda x: x["price"])
            
            # Store price history
            daily_manager = self.hass.data[DOMAIN].get("daily_manager")
            if daily_manager:
                await daily_manager.store_current_price(self.entry.entry_id, cheapest)
            
            return {
                "stations": stations,
                "cheapest": cheapest,
                "total_stations": len(stations),
            }
            
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
