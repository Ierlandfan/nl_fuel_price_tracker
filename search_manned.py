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
    if time_int == 0:
        return "00:00"
    if time_int == 2400:
        return "24:00"
    hours = time_int // 100
    minutes = time_int % 100
    return f"{hours:02d}:{minutes:02d}"

async def test_api():
    async with aiohttp.ClientSession() as session:
        lat = 52.0907
        lon = 5.1214
        radius = 20000
        
        places_url = f"{DIRECTLEASE_API_BASE}/places?latitude={lat}&longitude={lon}&radius={radius}&fmt=web&country=NL&lang=en"
        checksum = generate_checksum(places_url)
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "X-Checksum": checksum,
        }
        
        async with session.get(places_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
            places = await response.json() if response.status == 200 else []
        
        # Search for manned stations with shop
        for i, place in enumerate(places[:50]):
            station_id = place["id"]
            detail_url = f"{DIRECTLEASE_API_BASE}/places/{station_id}?_v48&lang=en"
            checksum = generate_checksum(detail_url)
            headers["X-Checksum"] = checksum
            
            async with session.get(detail_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    services = data.get("services", [])
                    
                    # Look for manned station with shop
                    if "shop" in services and "unmanned" not in services:
                        opening_times = data.get("openingTimes", [])
                        
                        print(f"\n{'='*80}")
                        print(f"🏪 {data.get('brand')} - {data.get('city')}")
                        print(f"📍 {data.get('address')}")
                        print(f"🏷️  Services: {', '.join(services)}")
                        print(f"\n📅 Opening Hours (RAW DATA):")
                        print(json.dumps(opening_times, indent=2))
                        
                        # Parse all opening time types
                        for schedule in opening_times:
                            types = schedule.get("types", [])
                            print(f"\n📝 Schedule for: {', '.join(types)}")
                            
                            days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                            
                            for day, name in zip(days, day_names):
                                if day in schedule:
                                    times = schedule[day]
                                    if times:
                                        start = format_time(times[0])
                                        end = format_time(times[1])
                                        print(f"  {name}: {start} - {end}")
                        
                        return  # Found one, stop

asyncio.run(test_api())
