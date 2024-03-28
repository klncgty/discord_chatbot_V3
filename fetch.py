
import aiohttp

async def fetch_image_data(url):
     async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
                return await response.read()

