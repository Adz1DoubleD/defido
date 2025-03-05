import os
import aiohttp


class Opensea:
    def __init__(self):
        self.url = "https://api.opensea.io/api/v2/"
        self.headers = {"X-API-KEY": os.getenv("OPENSEA_API_KEY")}

    async def make_request(self, endpoint: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.url + endpoint, headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def get_collection(self, slug):
        endpoint = f"collections/{slug}"
        return await self.make_request(endpoint)

    async def get_nft_id(self, nft, id, chain):
        endpoint = f"chain/{chain}/contract/{nft}/nfts/{id}"
        return await self.make_request(endpoint)

    async def get_collection_stats(self, slug):
        endpoint = f"collections/{slug}/stats"
        return await self.make_request(endpoint)
