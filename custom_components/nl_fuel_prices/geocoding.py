"""Geocoding for Dutch postcodes."""
from __future__ import annotations

import logging
import aiohttp
from typing import Any

_LOGGER = logging.getLogger(__name__)

PDOK_API = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free"


async def geocode_postcode(session: aiohttp.ClientSession, postcode: str) -> dict[str, Any] | None:
    """Geocode a Dutch postcode using PDOK (Dutch Government Official API)."""
    postcode_clean = postcode.strip().upper().replace(" ", "")
    
    if not postcode_clean:
        return None
    
    params = {
        "q": postcode_clean,
        "rows": 1,
        "fq": "type:postcode",
    }
    
    try:
        async with session.get(
            PDOK_API,
            params=params,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            if response.status != 200:
                _LOGGER.error(f"PDOK API returned status {response.status}")
                return None
            
            data = await response.json()
            
            docs = data.get("response", {}).get("docs", [])
            if not docs:
                _LOGGER.warning(f"No results for postcode: {postcode_clean}")
                return None
            
            result = docs[0]
            
            centroid = result.get("centroide_ll", "")
            if centroid.startswith("POINT("):
                coords = centroid.replace("POINT(", "").replace(")", "").split()
                longitude = float(coords[0])
                latitude = float(coords[1])
            else:
                _LOGGER.error(f"Invalid centroid format: {centroid}")
                return None
            
            return {
                "latitude": latitude,
                "longitude": longitude,
                "postcode": result.get("postcode", postcode_clean),
                "city": result.get("woonplaatsnaam"),
                "municipality": result.get("gemeentenaam"),
                "province": result.get("provincienaam"),
                "display_name": result.get("weergavenaam"),
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
