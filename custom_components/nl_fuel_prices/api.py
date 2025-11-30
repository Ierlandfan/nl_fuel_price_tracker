"""API client for Dutch fuel prices."""
from __future__ import annotations

import logging
from typing import Any
from datetime import datetime
import math

import aiohttp

_LOGGER = logging.getLogger(__name__)

TANKSERVICE_API = "https://tankservice.app-it-up.com/Tankservice/v1/places"

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
        """Get fuel prices for stations in radius from Tankservice API."""
        radius_meters = int(radius * 1000)
        api_fuel_type = FUEL_TYPE_MAP.get(fuel_type, fuel_type)
        
        url = f"{TANKSERVICE_API}?lat={latitude}&lng={longitude}&radius={radius_meters}"
        
        _LOGGER.debug(f"Fetching from Tankservice API: {url}")
        
        async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status != 200:
                _LOGGER.error(f"Tankservice API returned status {response.status}")
                raise Exception(f"API returned status {response.status}")
            
            data = await response.json()
            
            if not data or not isinstance(data, list):
                _LOGGER.warning("No data returned from Tankservice API")
                return []
            
            stations = []
            
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
                    
                    distance = self._calculate_distance(
                        latitude, longitude,
                        station_lat, station_lon
                    )
                    
                    station = {
                        "id": str(item.get("Id", f"station_{len(stations)}")),
                        "name": item.get("Name", "Unknown Station"),
                        "brand": item.get("Brand", "Unknown"),
                        "address": f"{item.get('Address', '')}, {item.get('City', '')}".strip(", "),
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
                    _LOGGER.debug(f"Skipping invalid station data: {err}")
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
