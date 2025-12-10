import asyncio
import aiohttp
import json
from custom_components.nl_fuel_prices.api import FuelPriceAPI

async def test():
    async with aiohttp.ClientSession() as session:
        api = FuelPriceAPI(session)
        # Test with a location in Medemblik
        stations = await api.get_fuel_prices(52.7713, 5.1039, 10, "euro95")
        if stations:
            print("First station data:")
            print(json.dumps(stations[0], indent=2))

asyncio.run(test())
