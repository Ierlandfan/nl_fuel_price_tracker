#!/usr/bin/env python3
import asyncio
import aiohttp
import json
import hashlib
import uuid
from datetime import datetime
from time import time

DIRECTLEASE_API_BASE = "https://tankservice.app-it-up.com/Tankservice/v2"

def generate_checksum(url):
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

async def test_api():
    async with aiohttp.ClientSession() as session:
        # First get places near Medemblik
        lat = 52.7713
        lon = 5.1039
        radius = 10000  # 10km
        
        places_url = f"{DIRECTLEASE_API_BASE}/places?latitude={lat}&longitude={lon}&radius={radius}&fmt=web&country=NL&lang=en"
        checksum = generate_checksum(places_url)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36",
            "Accept": "application/json",
            "X-Checksum": checksum,
        }
        
        print("Getting nearby stations...")
        async with session.get(places_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status != 200:
                print(f"Error getting places: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return
            
            places_data = await response.json()
            
            # Handle if it's a list directly or dict with places key
            if isinstance(places_data, list):
                places = places_data
            else:
                places = places_data.get("places", [])
            
            if not places:
                print("No stations found")
                return
            
            print(f"Found {len(places)} stations\n")
            
            # Get details for first station
            station_id = places[0]["id"]
            print(f"Getting details for station ID: {station_id}")
            
            detail_url = f"{DIRECTLEASE_API_BASE}/places/{station_id}?_v48&lang=en"
            checksum = generate_checksum(detail_url)
            
            headers["X-Checksum"] = checksum
            
            async with session.get(detail_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    print(f"Error getting details: {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
                    return
                
                detail_data = await response.json()
                
                print("\n" + "="*80)
                print("FULL STATION DATA:")
                print("="*80)
                print(json.dumps(detail_data, indent=2))
                print("\n" + "="*80)
                
                print("\nAVAILABLE FIELDS:")
                print("="*80)
                for key in detail_data.keys():
                    print(f"  - {key}")
                
                print("\n" + "="*80)
                print("CHECKING SPECIFIC FIELDS:")
                print("="*80)
                
                fields_to_check = [
                    "facilities", "voorzieningen", 
                    "unmanned", "onbemand",
                    "shop", "hasShop", "winkel",
                    "openingTimes", "openingstijden", "openingHours"
                ]
                
                for field in fields_to_check:
                    if field in detail_data:
                        print(f"✅ {field}: {detail_data[field]}")
                    else:
                        print(f"❌ {field}: NOT FOUND")

asyncio.run(test_api())
