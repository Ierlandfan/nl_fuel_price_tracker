"""API client for Dutch fuel prices using DirectLease Tank Service API."""
from __future__ import annotations

import logging
from typing import Any
from datetime import datetime
import math
import json
import hashlib
import uuid
from time import time

import aiohttp

_LOGGER = logging.getLogger(__name__)

# DirectLease Tank Service API - public mobile API
DIRECTLEASE_API_BASE = "https://tankservice.app-it-up.com/Tankservice/v2"
DIRECTLEASE_API_PLACES = f"{DIRECTLEASE_API_BASE}/places?fmt=web&country=NL&lang=en"

FUEL_TYPE_MAP = {
    "euro95": "E10",
    "euro98": "E5",
    "diesel": "B7",
    "lpg": "LPG",
    "adblue": "ADBLUE",
}


def _generate_checksum(url: str) -> str:
    """Generate DirectLease API checksum for authentication."""
    date_string = datetime.now().strftime("%Y%m%d")
    device_uuid = str(uuid.uuid4())
    date_uuid_part = f"{date_string}_{device_uuid}"
    timestamp = int(time())
    
    parts = url.split("/")
    file_path = "/".join(parts[3:])
    file_path = f"/{file_path}"
    
    base_string = f"{date_uuid_part}/{timestamp}/{file_path}/X-Checksum"
    hash_object = hashlib.sha1(base_string.encode("utf-8"))
    hashed = hash_object.hexdigest()
    
    return f"{date_uuid_part}/{timestamp}/{hashed}"


class FuelPriceAPI:
    """API client for Dutch fuel price data using DirectLease Tank Service."""

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
        """Get fuel prices using the DirectLease Tank Service API."""
        
        api_fuel_type = FUEL_TYPE_MAP.get(fuel_type, fuel_type.upper())
        
        # DirectLease API endpoint
        url = DIRECTLEASE_API_PLACES
        
        _LOGGER.debug(f"Fetching from DirectLease Tank Service API: {url}")
        
        # Generate authentication checksum
        checksum = _generate_checksum(url)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
            "Accept": "application/json",
            "X-Checksum": checksum,
        }
        
        try:
            async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_directlease_data(data, latitude, longitude, radius, fuel_type)
                elif response.status == 403:
                    _LOGGER.error("DirectLease API blocked request - IP may be blocked. Contact tankservice-block@app-it-up.com")
                    return []
                else:
                    _LOGGER.warning(f"DirectLease API returned status {response.status}")
                    text = await response.text()
                    _LOGGER.debug(f"Response: {text[:200]}")
                    return []
        except aiohttp.ClientError as err:
            _LOGGER.error(f"DirectLease API connection error: {err}")
            return []
        except Exception as err:
            _LOGGER.error(f"DirectLease API failed: {err}")
            return []
    
    async def _parse_directlease_data(
        self,
        data: Any,
        latitude: float,
        longitude: float,
        radius: float,
        fuel_type: str,
    ) -> list[dict[str, Any]]:
        """Parse DirectLease Tank Service API response."""
        stations = []
        
        if not data or not isinstance(data, list):
            _LOGGER.debug(f"Invalid data format: {type(data)}")
            return stations
        
        api_fuel_type = FUEL_TYPE_MAP.get(fuel_type, fuel_type.upper())
        
        _LOGGER.debug(f"Processing {len(data)} stations from API")
        
        for item in data:
            try:
                # Get coordinates
                station_lat = item.get("latitude")
                station_lon = item.get("longitude")
                
                if station_lat is None or station_lon is None:
                    continue
                
                # Calculate distance
                distance = self._calculate_distance(latitude, longitude, station_lat, station_lon)
                
                if distance > radius:
                    continue
                
                # Find matching fuel price
                fuels = item.get("fuels", [])
                matching_price = None
                
                for fuel_item in fuels:
                    fuel_name = fuel_item.get("name", "")
                    # Extract fuel type from name like "Euro 95 (E10)"
                    if api_fuel_type.lower() in fuel_name.lower() or f"({api_fuel_type})" in fuel_name:
                        price_value = fuel_item.get("price")
                        if price_value and price_value > 0:
                            # DirectLease returns price in cents per liter (e.g., 1899 = €1.899)
                            matching_price = price_value / 1000
                            break
                
                if matching_price is None or matching_price == 0:
                    continue
                
                # Build station data
                station = {
                    "id": str(item.get("id", f"station_{len(stations)}")),
                    "name": item.get("name", "Unknown Station"),
                    "brand": item.get("brand", "Unknown"),
                    "address": f"{item.get('address', '')}, {item.get('city', '')} {item.get('postalCode', '')}".strip(", "),
                    "latitude": station_lat,
                    "longitude": station_lon,
                    "fuel_type": fuel_type,
                    "price": round(matching_price, 3),
                    "opening_hours": self._parse_opening_hours(item.get("openingTimes", [])),
                    "last_updated": datetime.now().isoformat(),
                    "distance": round(distance, 2),
                }
                
                stations.append(station)
                
            except (KeyError, ValueError, TypeError) as err:
                _LOGGER.debug(f"Skipping invalid station: {err}")
                continue
        
        # Sort by price (cheapest first)
        stations.sort(key=lambda x: x["price"])
        
        # Add ranking
        for idx, station in enumerate(stations, 1):
            station["rank"] = idx
        
        _LOGGER.debug(f"Found {len(stations)} stations within {radius}km with {fuel_type} prices")
        
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
