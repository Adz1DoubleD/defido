import aiohttp


class Coingecko:
    def __init__(self):
        self.url = "https://api.coingecko.com/api/v3/"

    async def search(self, token):
        endpoint = f"search?query={token}"
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + endpoint) as response:
                return await response.json()

    async def get_mcap(self, token):
        endpoint = f"simple/price?ids={token}&vs_currencies=usd&include_market_cap=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + endpoint) as response:
                data = await response.json()
                return data[token]["usd_market_cap"]
