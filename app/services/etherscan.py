import aiohttp
import os
import time

from bot import constants


class Etherscan:
    def __init__(self):
        self.url = f"https://api.etherscan.io/v2/api?chainid={constants.CHAIN_ID}"
        self.key = os.getenv("ETHERSCAN_API_KEY")

    async def make_request(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def get_block(self, time: int) -> str:
        url = f"{self.url}&module=block&action=getblocknobytime&timestamp={time}&closest=before&apikey={self.key}"
        data = await self.make_request(url)
        return data["result"] if data else None

    async def get_daily_tx_count(self, contract: str) -> int:
        yesterday = int(time.time()) - 86400
        block_yesterday = await self.get_block(yesterday)
        block_now = await self.get_block(int(time.time()))

        tx_url = f"{self.url}&module=account&action=txlist&address={contract}&startblock={block_yesterday}&endblock={block_now}&page=1&offset=1000&sort=asc&apikey={self.key}"
        tx_data = await self.make_request(tx_url)
        tx_entry_count = (
            len(tx_data["result"]) if tx_data and "result" in tx_data else 0
        )

        internal_tx_url = f"{self.url}&module=account&action=txlist&address={contract}&startblock={block_yesterday}&endblock={block_now}&page=1&offset=1000&sort=asc&apikey={self.key}"
        internal_tx_data = await self.make_request(internal_tx_url)
        internal_tx_entry_count = (
            len(internal_tx_data["result"])
            if internal_tx_data and "result" in internal_tx_data
            else 0
        )

        return tx_entry_count + internal_tx_entry_count

    async def get_gas(self):
        url = f"{self.url}&module=gastracker&action=gasoracle&apikey={self.key}"
        return await self.make_request(url)

    async def get_native_balance(self, wallet):
        url = f"{self.url}&module=account&action=balancemulti&address={wallet}&tag=latest&apikey={self.key}"
        data = await self.make_request(url)

        if not data or "result" not in data:
            return "0.00"

        amount = int(data["result"][0]["balance"]) / 10**18
        if "e-" in str(amount):
            return "{:.8f}".format(amount)
        elif amount < 1:
            return "{:.8f}".format(amount)
        else:
            return "{:.2f}".format(amount)

    async def get_native_price(self, token):
        url = f"{self.url}&module=stats&action={token}price&apikey={self.key}"
        data = await self.make_request(url)
        if data and "result" in data:
            return float(data["result"]["ethusd"])
        return 0.0

    async def get_token_balance(self, wallet, token, decimals):
        url = f"{self.url}&module=account&action=tokenbalance&contractaddress={token}&address={wallet}&tag=latest&apikey={self.key}"
        data = await self.make_request(url)
        if data and "result" in data and int(data["result"]):
            return int(data["result"][: -int(decimals)])
        return 0
