"""Sensor platform for Dutch Fuel Prices."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CURRENCY_EURO

from . import FuelPriceCoordinator
from .const import (
    DOMAIN,
    FUEL_TYPES,
    ATTR_STATION_NAME,
    ATTR_STATION_BRAND,
    ATTR_STATION_ADDRESS,
    ATTR_DISTANCE,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_OPENING_HOURS,
    ATTR_LAST_UPDATED,
    ATTR_RANK,
    ATTR_TOTAL_STATIONS,
    ATTR_STATION_ID,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: FuelPriceCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    fuel_type = entry.data.get("fuel_type", "euro95")
    location_name = entry.data.get("location_name", "Unknown")
    
    async_add_entities([
        FuelPriceSensor(coordinator, fuel_type, location_name)
    ])


class FuelPriceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a fuel price sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/L"

    def __init__(
        self,
        coordinator: FuelPriceCoordinator,
        fuel_type: str,
        location_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._fuel_type = fuel_type
        self._location_name = location_name
        self._attr_unique_id = f"{DOMAIN}_{fuel_type}_{location_name}"
        self._attr_name = f"Fuel {FUEL_TYPES.get(fuel_type, fuel_type)} {location_name}"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor (cheapest price)."""
        cheapest = self.coordinator.data.get("cheapest")
        if cheapest:
            return cheapest.get("price")
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        cheapest = self.coordinator.data.get("cheapest")
        if not cheapest:
            return {}
        
        return {
            ATTR_STATION_NAME: cheapest.get("name"),
            ATTR_STATION_BRAND: cheapest.get("brand"),
            ATTR_STATION_ADDRESS: cheapest.get("address"),
            ATTR_DISTANCE: cheapest.get("distance"),
            ATTR_LATITUDE: cheapest.get("latitude"),
            ATTR_LONGITUDE: cheapest.get("longitude"),
            ATTR_OPENING_HOURS: cheapest.get("opening_hours"),
            ATTR_LAST_UPDATED: cheapest.get("last_updated"),
            ATTR_RANK: 1,  # Always 1 as this is the cheapest
            ATTR_TOTAL_STATIONS: self.coordinator.data.get("total_stations", 0),
            ATTR_STATION_ID: cheapest.get("id"),
            "fuel_type": FUEL_TYPES.get(self._fuel_type, self._fuel_type),
            "location_postcode": self.coordinator.entry.data.get("town_postcode"),
            "location_province": self.coordinator.entry.data.get("town_province"),
        }

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return "mdi:gas-station"
