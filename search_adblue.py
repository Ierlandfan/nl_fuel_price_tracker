import asyncio
import aiohttp
import hashlib
import uuid
from datetime import datetime
from time import time

def _generate_checksum(url: str) -> str:
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

async def search_adblue():
    url = "https://tankservice.app-it-up.com/Tankservice/v2/places?fmt=web&country=NL&lang=en"
    
    async with aiohttp.ClientSession() as session:
        checksum = _generate_checksum(url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
            "Accept": "application/json",
            "X-Checksum": checksum,
        }
        
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
            if response.status == 200:
                data = await response.json()
                print(f"Testing {min(50, len(data))} stations for AdBlue...")
                
                found_adblue = False
                
                # Test first 50 stations
                for i in range(min(50, len(data))):
                    station_id = data[i]["id"]
                    detail_url = f"https://tankservice.app-it-up.com/Tankservice/v2/places/{station_id}?_v48&lang=en"
                    detail_checksum = _generate_checksum(detail_url)
                    detail_headers = {
                        "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
                        "Accept": "application/json",
                        "X-Checksum": detail_checksum,
                    }
                    
                    async with session.get(detail_url, headers=detail_headers, timeout=aiohttp.ClientTimeout(total=10)) as detail_response:
                        if detail_response.status == 200:
                            detail_data = await detail_response.json()
                            fuels = detail_data.get("fuels", [])
                            for fuel in fuels:
                                key = fuel.get('key', '').lower()
                                if 'adblue' in key or 'ad' in key or 'blue' in key:
                                    found_adblue = True
                                    print(f"\n✅ Found AdBlue at station {station_id} ({data[i].get('brand')}):")
                                    print(f"   All fuels: {[f.get('key') for f in fuels]}")
                                    break
                
                if not found_adblue:
                    print("\n❌ AdBlue not found in first 50 stations")
                    print("AdBlue might not be available in the DirectLease API")

asyncio.run(search_adblue())
