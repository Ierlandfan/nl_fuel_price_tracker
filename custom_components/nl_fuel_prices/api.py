"""API client for Dutch fuel prices using United Consumers public API."""
from __future__ import annotations

import logging
from typing import Any
from datetime import datetime
import math
import json

import aiohttp

_LOGGER = logging.getLogger(__name__)

# United Consumers has a public mobile API endpoint
UC_API_URL = "https://www.unitedconsumers.com/tanken/v1/stations"

FUEL_TYPE_MAP = {
    "euro95": "euro95",
    "euro98": "super",
    "diesel": "diesel",
    "lpg": "lpg",
    "adblue": "adblue",
}


class FuelPriceAPI:
    """API client for Dutch fuel price data."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self.session = session

    async def get_fuel_prices(
        self,
        latitude: float,
        longitude: float,
        radius: float,
        fuel_type: str,
    ) -> list[dict[str, Any]]:
        """Get fuel prices using the Tankservice.nl public mobile API."""
        
        # Try the mobile app API endpoint first
        api_fuel_type = FUEL_TYPE_MAP.get(fuel_type, fuel_type)
        
        # Tankservice.nl mobile app uses this endpoint
        url = f"https://api.tankservice.nl/v1/locations?latitude={latitude}&longitude={longitude}&radius={int(radius * 1000)}&fuelType={api_fuel_type}"
        
        _LOGGER.debug(f"Fetching from Tankservice API: {url}")
        
        headers = {
            "User-Agent": "HomeAssistant/1.0",
            "Accept": "application/json",
        }
        
        try:
            async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_tankservice_data(data, latitude, longitude, radius, fuel_type)
                else:
                    _LOGGER.warning(f"Tankservice API returned {response.status}, trying fallback")
        except Exception as err:
            _LOGGER.warning(f"Tankservice API failed: {err}, trying fallback")
        
        # Fallback: Try DirectLease API (might work without key for limited requests)
        return await self._fallback_directlease(latitude, longitude, radius, fuel_type)
    
    async def _parse_tankservice_data(
        self,
        data: Any,
        latitude: float,
        longitude: float,
        radius: float,
        fuel_type: str,
    ) -> list[dict[str, Any]]:
        """Parse Tankservice API response."""
        stations = []
        
        if not data or not isinstance(data, (list, dict)):
            return stations
        
        # Handle different response formats
        location_list = data if isinstance(data, list) else data.get("locations", data.get("stations", []))
        
        for item in location_list:
            try:
                station_lat = float(item.get("latitude", item.get("lat", 0)))
                station_lon = float(item.get("longitude", item.get("lng", item.get("lon", 0))))
                
                if station_lat == 0 or station_lon == 0:
                    continue
                
                # Find price for requested fuel type
                price = None
                prices_data = item.get("prices", item.get("fuels", []))
                
                if isinstance(prices_data, dict):
                    price = prices_data.get(fuel_type)
                elif isinstance(prices_data, list):
                    for price_item in prices_data:
                        if price_item.get("type", "").lower() == fuel_type.lower():
                            price = price_item.get("price")
                            break
                
                if price is None or price == 0:
                    continue
                
                distance = self._calculate_distance(latitude, longitude, station_lat, station_lon)
                
                if distance > radius:
                    continue
                
                station = {
                    "id": str(item.get("id", f"station_{len(stations)}")),
                    "name": item.get("name", item.get("title", "Unknown Station")),
                    "brand": item.get("brand", "Unknown"),
                    "address": item.get("address", ""),
                    "latitude": station_lat,
                    "longitude": station_lon,
                    "fuel_type": fuel_type,
                    "price": float(price),
                    "opening_hours": item.get("openingHours", "Unknown"),
                    "last_updated": datetime.now().isoformat(),
                    "distance": round(distance, 2),
                }
                
                stations.append(station)
                
            except (KeyError, ValueError, TypeError) as err:
                _LOGGER.debug(f"Skipping invalid station: {err}")
                continue
        
        stations.sort(key=lambda x: x["price"])
        
        for idx, station in enumerate(stations, 1):
            station["rank"] = idx
        
        return stations
    
    async def _fallback_directlease(
        self,
        latitude: float,
        longitude: float,
        radius: float,
        fuel_type: str,
    ) -> list[dict[str, Any]]:
        """Fallback to DirectLease API (may require key but try anyway)."""
        
        api_fuel_type = FUEL_TYPE_MAP.get(fuel_type, fuel_type)
        radius_meters = int(radius * 1000)
        
        url = f"https://tankservice.app-it-up.com/Tankservice/v1/places?lat={latitude}&lng={longitude}&radius={radius_meters}"
        
        _LOGGER.debug(f"Trying DirectLease fallback: {url}")
        
        headers = {
            "User-Agent": "HomeAssistant/1.0",
            "Accept": "application/json",
        }
        
        try:
            async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_directlease_data(data, latitude, longitude, radius, fuel_type)
                else:
                    _LOGGER.error(f"DirectLease API returned {response.status} - API key may be required")
                    return []
        except Exception as err:
            _LOGGER.error(f"DirectLease fallback failed: {err}")
            return []
    
    async def _parse_directlease_data(
        self,
        data: Any,
        latitude: float,
        longitude: float,
        radius: float,
        fuel_type: str,
    ) -> list[dict[str, Any]]:
        """Parse DirectLease API response."""
        stations = []
        
        if not data or not isinstance(data, list):
            return stations
        
        api_fuel_type = FUEL_TYPE_MAP.get(fuel_type, fuel_type)
        
        for item in data:
            try:
                prices = item.get("Fuels", [])
                matching_price = None
                
                for price_item in prices:
                    if price_item.get("FuelType", "").lower() == api_fuel_type.lower():
                        matching_price = price_item.get("Price")
                        break
                
                if matching_price is None:
                    continue
                
                station_lat = item.get("Latitude")
                station_lon = item.get("Longitude")
                
                if station_lat is None or station_lon is None:
                    continue
                
                distance = self._calculate_distance(latitude, longitude, station_lat, station_lon)
                
                if distance > radius:
                    continue
                
                station = {
                    "id": str(item.get("Id", f"station_{len(stations)}")),
                    "name": item.get("Name", "Unknown Station"),
                    "brand": item.get("Brand", "Unknown"),
                    "address": f"{item.get('Street', '')} {item.get('HouseNumber', '')}, {item.get('City', '')}".strip(),
                    "latitude": station_lat,
                    "longitude": station_lon,
                    "fuel_type": fuel_type,
                    "price": float(matching_price),
                    "opening_hours": self._parse_opening_hours(item.get("OpeningTimes", [])),
                    "last_updated": datetime.now().isoformat(),
                    "distance": round(distance, 2),
                }
                
                stations.append(station)
                
            except (KeyError, ValueError, TypeError) as err:
                _LOGGER.debug(f"Skipping invalid DirectLease station: {err}")
                continue
        
        stations.sort(key=lambda x: x["price"])
        
        for idx, station in enumerate(stations, 1):
            station["rank"] = idx
        
        return stations
    
    def _parse_opening_hours(self, opening_times: list) -> str:
        """Parse opening hours from API format."""
        if not opening_times:
            return "Unknown"
        
        try:
            today = datetime.now().weekday()
            
            for day_hours in opening_times:
                if day_hours.get("Day") == today:
                    open_time = day_hours.get("Open", "")
                    close_time = day_hours.get("Close", "")
                    
                    if open_time and close_time:
                        return f"{open_time}-{close_time}"
            
            return "See website"
        except Exception:
            return "Unknown"

    def _calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two coordinates in km using Haversine formula."""
        R = 6371
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
