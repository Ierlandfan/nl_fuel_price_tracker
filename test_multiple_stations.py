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
        lat = 52.7713
        lon = 5.1039
        radius = 10000
        
        places_url = f"{DIRECTLEASE_API_BASE}/places?latitude={lat}&longitude={lon}&radius={radius}&fmt=web&country=NL&lang=en"
        checksum = generate_checksum(places_url)
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "X-Checksum": checksum,
        }
        
        async with session.get(places_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
            places = await response.json() if response.status == 200 else []
            
        all_services = set()
        
        # Check first 10 stations
        for i, place in enumerate(places[:10]):
            station_id = place["id"]
            detail_url = f"{DIRECTLEASE_API_BASE}/places/{station_id}?_v48&lang=en"
            checksum = generate_checksum(detail_url)
            headers["X-Checksum"] = checksum
            
            async with session.get(detail_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    services = data.get("services", [])
                    all_services.update(services)
                    print(f"{i+1}. {data.get('brand')} {data.get('city')}: {services}")
        
        print(f"\n\n🎯 ALL UNIQUE SERVICES FOUND:")
        for service in sorted(all_services):
            print(f"  - {service}")

asyncio.run(test_api())
