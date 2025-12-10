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

def format_time(time_int):
    """Convert time like 800 to '08:00', 1630 to '16:30'"""
    if time_int == 0:
        return "00:00"
    if time_int == 2400:
        return "24:00"
    
    hours = time_int // 100
    minutes = time_int % 100
    return f"{hours:02d}:{minutes:02d}"

def format_opening_hours(opening_times):
    """Format opening hours for display"""
    if not opening_times:
        return "Unknown"
    
    result = []
    for schedule in opening_times:
        types = schedule.get("types", [])
        
        days = {
            "mon": "Monday",
            "tue": "Tuesday", 
            "wed": "Wednesday",
            "thu": "Thursday",
            "fri": "Friday",
            "sat": "Saturday",
            "sun": "Sunday"
        }
        
        for day_key, day_name in days.items():
            if day_key in schedule:
                times = schedule[day_key]
                if times:
                    if len(times) == 2:
                        start = format_time(times[0])
                        end = format_time(times[1])
                        result.append(f"{day_name}: {start} - {end}")
    
    return "\n".join(result)

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
        
        # Check first 5 stations
        for i, place in enumerate(places[:5]):
            station_id = place["id"]
            detail_url = f"{DIRECTLEASE_API_BASE}/places/{station_id}?_v48&lang=en"
            checksum = generate_checksum(detail_url)
            headers["X-Checksum"] = checksum
            
            async with session.get(detail_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    services = data.get("services", [])
                    opening_times = data.get("openingTimes", [])
                    
                    print(f"\n{'='*80}")
                    print(f"🏪 {data.get('brand')} - {data.get('city')}")
                    print(f"📍 {data.get('address')}")
                    print(f"🏷️  Services: {', '.join(services) if services else 'None'}")
                    
                    is_unmanned = "unmanned" in services
                    is_24_7 = "gas247" in services
                    has_shop = "shop" in services
                    
                    print(f"\n{'Unmanned' if is_unmanned else 'Manned'} station")
                    if has_shop:
                        print("✅ Has shop")
                    if is_24_7:
                        print("🕐 Open 24/7")
                    
                    print(f"\n📅 Opening Hours:")
                    print(format_opening_hours(opening_times))
                    
                    print(f"\nRaw data: {json.dumps(opening_times, indent=2)}")

asyncio.run(test_api())
