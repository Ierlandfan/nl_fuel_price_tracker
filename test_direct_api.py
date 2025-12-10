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

async def test():
    async with aiohttp.ClientSession() as session:
        # Get a station near Medemblik
        detail_url = f"{DIRECTLEASE_API_BASE}/places/5274?_v48&lang=en"
        checksum = generate_checksum(detail_url)
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "X-Checksum": checksum,
        }
        
        async with session.get(detail_url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print("Available fields in station detail:")
                print(json.dumps(data, indent=2))

asyncio.run(test())
