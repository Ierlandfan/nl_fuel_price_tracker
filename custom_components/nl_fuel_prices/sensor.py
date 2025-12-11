"""Sensor platform for Dutch Fuel Prices."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
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
    postcode = entry.data.get("postcode", location_name)  # Fallback to location_name for old configs
    
    sensors = [
        FuelPriceSensor(coordinator, fuel_type, location_name, postcode, is_main=True)
    ]
    
    # Dynamically add sensors based on actual stations found (up to max 5 total)
    stations = coordinator.data.get("stations", [])
    num_stations = min(len(stations), 5)  # Max 5 stations total
    
    # Add sensors for alternative stations (stations 1 onwards, as station 0 is the main/cheapest)
    for i in range(1, num_stations):
        sensors.append(
            FuelStationSensor(coordinator, fuel_type, location_name, postcode, i)
        )
    
    async_add_entities(sensors)


class FuelPriceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a fuel price sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/L"

    def __init__(
        self,
        coordinator: FuelPriceCoordinator,
        fuel_type: str,
        location_name: str,
        postcode: str,
        is_main: bool = False,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._fuel_type = fuel_type
        self._location_name = location_name
        self._is_main = is_main
        self._attr_unique_id = f"{DOMAIN}_{fuel_type}_{postcode}"
        self._attr_name = f"{location_name} - {FUEL_TYPES.get(fuel_type, fuel_type)}"
        self._attr_entity_registry_enabled_default = True  # Explicitly enable
        
        # Set up device info for grouping
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{fuel_type}_{postcode}")},
            name=f"{location_name} - {FUEL_TYPES.get(fuel_type, fuel_type)}",
            manufacturer="DirectLease",
            model="Fuel Price Tracker",
            entry_type="service",
        )

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor (cheapest price)."""
        cheapest = self.coordinator.data.get("cheapest")
        if cheapest:
            return cheapest.get("price")
        return None
    
    @property
    def name(self) -> str:
        """Return the name with station name and distance if available."""
        cheapest = self.coordinator.data.get("cheapest")
        if cheapest and self._is_main:
            station_name = cheapest.get("name", "Unknown")
            distance = cheapest.get("distance")
            if distance is not None:
                return f"{station_name} ({distance}km) - {FUEL_TYPES.get(self._fuel_type, self._fuel_type)}"
            return f"{station_name} ({FUEL_TYPES.get(self._fuel_type, self._fuel_type)})"
        return self._attr_name

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        cheapest = self.coordinator.data.get("cheapest")
        if not cheapest:
            return {}
        
        # Get all stations for display
        all_stations = self.coordinator.data.get("stations", [])
        
        attributes = {
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
            "radius": self.coordinator.entry.data.get("radius", 10),
            # Services information
            "is_unmanned": cheapest.get("is_unmanned", False),
            "has_shop": cheapest.get("has_shop", False),
            "services": cheapest.get("services", []),
            "shop_hours": cheapest.get("shop_hours"),
        }
        
        # Add alternative stations (top 5)
        if len(all_stations) > 1:
            alternatives = []
            for idx, station in enumerate(all_stations[1:6], 2):  # Stations 2-6
                alternatives.append({
                    "rank": idx,
                    "name": station.get("name"),
                    "brand": station.get("brand"),
                    "price": station.get("price"),
                    "distance": station.get("distance"),
                    "address": station.get("address"),
                    "is_unmanned": station.get("is_unmanned", False),
                    "has_shop": station.get("has_shop", False),
                    "services": station.get("services", []),
                })
            attributes["alternatives"] = alternatives
            attributes["alternative_count"] = len(alternatives)
        
        return attributes

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return "mdi:gas-station"


class FuelStationSensor(CoordinatorEntity, SensorEntity):
    """Representation of an individual fuel station sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/L"

    def __init__(
        self,
        coordinator: FuelPriceCoordinator,
        fuel_type: str,
        location_name: str,
        postcode: str,
        index: int,
    ) -> None:
        """Initialize the station sensor."""
        super().__init__(coordinator)
        self._fuel_type = fuel_type
        self._location_name = location_name
        self._index = index
        self._attr_unique_id = f"{DOMAIN}_{fuel_type}_{postcode}_station_{index}"
        self._attr_entity_registry_enabled_default = True  # Explicitly enable all stations
        
        # Set up device info for grouping (same device as main sensor)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{fuel_type}_{postcode}")},
            name=f"{location_name} - {FUEL_TYPES.get(fuel_type, fuel_type)}",
            manufacturer="DirectLease",
            model="Fuel Price Tracker",
            entry_type="service",
        )

    @property
    def native_value(self) -> float | None:
        """Return the price of this station."""
        stations = self.coordinator.data.get("stations", [])
        if self._index < len(stations):
            return stations[self._index].get("price")
        return None

    @property
    def name(self) -> str:
        """Return the name with station name and distance."""
        stations = self.coordinator.data.get("stations", [])
        if self._index < len(stations):
            station = stations[self._index]
            station_name = station.get("name", f"Station {self._index + 1}")
            distance = station.get("distance")
            if distance is not None:
                return f"{station_name} ({distance}km) - {FUEL_TYPES.get(self._fuel_type, self._fuel_type)}"
            return f"{station_name} ({FUEL_TYPES.get(self._fuel_type, self._fuel_type)})"
        return f"Fuel Station {self._index + 1} {self._location_name}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        stations = self.coordinator.data.get("stations", [])
        return self._index < len(stations)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        stations = self.coordinator.data.get("stations", [])
        if self._index >= len(stations):
            return {}

        station = stations[self._index]
        return {
            ATTR_STATION_NAME: station.get("name"),
            ATTR_STATION_BRAND: station.get("brand"),
            ATTR_STATION_ADDRESS: station.get("address"),
            ATTR_DISTANCE: station.get("distance"),
            ATTR_LATITUDE: station.get("latitude"),
            ATTR_LONGITUDE: station.get("longitude"),
            ATTR_OPENING_HOURS: station.get("opening_hours"),
            ATTR_RANK: self._index + 1,
            "fuel_type": FUEL_TYPES.get(self._fuel_type, self._fuel_type),
            "location_postcode": self.coordinator.entry.data.get("town_postcode"),
            "location_province": self.coordinator.entry.data.get("town_province"),
            # Services information
            "is_unmanned": station.get("is_unmanned", False),
            "has_shop": station.get("has_shop", False),
            "services": station.get("services", []),
            "shop_hours": station.get("shop_hours"),
        }

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return "mdi:gas-station-outline"
