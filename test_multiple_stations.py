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

async def test_stations():
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
                
                fuel_keys_seen = set()
                
                # Test first 10 stations
                for i in range(min(10, len(data))):
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
                            if fuels:
                                print(f"\nStation {station_id} ({data[i].get('brand')}):")
                                for fuel in fuels:
                                    key = fuel.get('key')
                                    fuel_keys_seen.add(key)
                                    print(f"  {key}: {fuel.get('name')} = €{fuel.get('price')/1000:.3f}")
                
                print(f"\n\nAll unique fuel keys seen: {fuel_keys_seen}")

asyncio.run(test_stations())
