"""Geocoding for Dutch postcodes."""
from __future__ import annotations

import logging
import aiohttp
from typing import Any

_LOGGER = logging.getLogger(__name__)

NOMINATIM_API = "https://nominatim.openstreetmap.org/search"


async def geocode_postcode(session: aiohttp.ClientSession, postcode: str) -> dict[str, Any] | None:
    """Geocode a Dutch postcode using Nominatim (OpenStreetMap)."""
    postcode_clean = postcode.strip().upper()
    
    if not postcode_clean:
        return None
    
    query = f"{postcode_clean}, Netherlands"
    
    params = {
        "q": query,
        "format": "json",
        "countrycodes": "nl",
        "limit": 1,
        "addressdetails": 1,
    }
    
    headers = {
        "User-Agent": "HomeAssistant-NL-Fuel-Prices/1.0"
    }
    
    try:
        async with session.get(
            NOMINATIM_API,
            params=params,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            if response.status != 200:
                _LOGGER.error(f"Nominatim API returned status {response.status}")
                return None
            
            data = await response.json()
            
            if not data or len(data) == 0:
                _LOGGER.warning(f"No results for postcode: {postcode_clean}")
                return None
            
            result = data[0]
            address = result.get("address", {})
            
            return {
                "latitude": float(result["lat"]),
                "longitude": float(result["lon"]),
                "postcode": postcode_clean,
                "city": address.get("city") or address.get("town") or address.get("village") or address.get("municipality"),
                "municipality": address.get("municipality"),
                "province": address.get("state"),
                "display_name": result.get("display_name"),
            }
            
    except Exception as err:
        _LOGGER.error(f"Error geocoding postcode {postcode_clean}: {err}")
        return None


def validate_dutch_postcode(postcode: str) -> bool:
    """Validate Dutch postcode format (1234 AB or 1234AB)."""
    postcode_clean = postcode.strip().upper().replace(" ", "")
    
    if len(postcode_clean) != 6:
        return False
    
    if not postcode_clean[:4].isdigit():
        return False
    
    if not postcode_clean[4:].isalpha():
        return False
    
    return True
