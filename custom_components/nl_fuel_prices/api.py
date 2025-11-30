"""API client for Dutch fuel prices."""
from __future__ import annotations

import logging
from typing import Any
from datetime import datetime
import math

import aiohttp

_LOGGER = logging.getLogger(__name__)


class FuelPriceAPI:
    """API client for Dutch fuel price data."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self.session = session
        self._cache: dict[str, Any] = {}

    async def get_fuel_prices(
        self,
        latitude: float,
        longitude: float,
        radius: float,
        fuel_type: str,
    ) -> list[dict[str, Any]]:
        """
        Get fuel prices for stations in radius.
        
        Currently uses a mock/demo data source.
        Real implementation will use DirectLease or United Consumers API.
        """
        try:
            # TODO: Implement real API calls
            # For now, return mock data for testing
            return await self._get_mock_data(latitude, longitude, radius, fuel_type)
            
        except Exception as err:
            _LOGGER.error(f"Error fetching fuel prices: {err}")
            return []

    async def _get_mock_data(
        self,
        latitude: float,
        longitude: float,
        radius: float,
        fuel_type: str,
    ) -> list[dict[str, Any]]:
        """
        Return mock data for testing.
        
        This will be replaced with real API calls to:
        - DirectLease API (preferred)
        - United Consumers API (fallback)
        - Web scraping (last resort)
        """
        # Mock fuel stations around given coordinates
        stations = [
            {
                "id": "shell_ede_001",
                "name": "Shell Ede Centrum",
                "brand": "Shell",
                "address": "Hoofdstraat 123, 6711 AA Ede",
                "latitude": latitude + 0.01,
                "longitude": longitude + 0.01,
                "fuel_type": fuel_type,
                "price": 1.859,  # EUR per liter
                "opening_hours": "06:00-23:00",
                "last_updated": datetime.now().isoformat(),
            },
            {
                "id": "bp_veenendaal_002",
                "name": "BP Veenendaal",
                "brand": "BP",
                "address": "Kerkstraat 45, 3901 AB Veenendaal",
                "latitude": latitude + 0.02,
                "longitude": longitude - 0.01,
                "fuel_type": fuel_type,
                "price": 1.879,
                "opening_hours": "00:00-24:00",
                "last_updated": datetime.now().isoformat(),
            },
            {
                "id": "tango_wageningen_003",
                "name": "Tango Wageningen",
                "brand": "Tango",
                "address": "Stationsstraat 67, 6701 AM Wageningen",
                "latitude": latitude - 0.01,
                "longitude": longitude + 0.02,
                "fuel_type": fuel_type,
                "price": 1.839,  # Cheapest!
                "opening_hours": "07:00-22:00",
                "last_updated": datetime.now().isoformat(),
            },
            {
                "id": "esso_ede_004",
                "name": "Esso Ede Noord",
                "brand": "Esso",
                "address": "Verlengde Hoge Veenweg 89, 6717 KK Ede",
                "latitude": latitude + 0.015,
                "longitude": longitude + 0.015,
                "fuel_type": fuel_type,
                "price": 1.869,
                "opening_hours": "06:00-22:00",
                "last_updated": datetime.now().isoformat(),
            },
            {
                "id": "texaco_veenendaal_005",
                "name": "Texaco Veenendaal West",
                "brand": "Texaco",
                "address": "Parallelweg 12, 3905 NL Veenendaal",
                "latitude": latitude + 0.025,
                "longitude": longitude - 0.015,
                "fuel_type": fuel_type,
                "price": 1.889,
                "opening_hours": "00:00-24:00",
                "last_updated": datetime.now().isoformat(),
            },
        ]

        # Calculate distance and filter by radius
        result = []
        for station in stations:
            distance = self._calculate_distance(
                latitude,
                longitude,
                station["latitude"],
                station["longitude"],
            )
            
            if distance <= radius:
                station["distance"] = round(distance, 2)
                result.append(station)

        # Sort by price (cheapest first)
        result.sort(key=lambda x: x["price"])
        
        # Add rank
        for idx, station in enumerate(result, 1):
            station["rank"] = idx

        return result

    def _calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two coordinates in km using Haversine formula."""
        R = 6371  # Earth's radius in kilometers

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

    async def search_station(self, query: str) -> list[dict[str, Any]]:
        """Search for fuel stations by name or address."""
        # TODO: Implement station search
        return []


# API Implementation Notes:
# 
# DirectLease API (Preferred):
# - Endpoint: https://tankservice.app-it-up.com/Tankservice/v1/places
# - Requires API key (free tier available)
# - Real-time prices for Netherlands
# - Good coverage of major brands
#
# United Consumers (Fallback):
# - Endpoint: https://www.unitedconsumers.com/tanken/informatie/
# - Community-reported prices
# - May require web scraping
# - Good for price comparison
#
# Implementation priority:
# 1. Add DirectLease API integration (requires API key registration)
# 2. Add United Consumers scraping as fallback
# 3. Add Benzineprijs.nl as additional source
# 4. Merge data from multiple sources for best accuracy
