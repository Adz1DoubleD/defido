import os
import requests
import time

from bot import constants


class Etherscan:
    def __init__(self):
        self.url = f"https://api.etherscan.io/v2/api?chainid={constants.CHAIN_ID}"
        self.key = os.getenv("ETHERSCAN_API_KEY")

    def get_block(self, time: "int") -> str:
        url = f"{self.url}&module=block&action=getblocknobytime&timestamp={time}&closest=before&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return data["result"]

    def get_daily_tx_count(self, contract: str) -> int:
        yesterday = int(time.time()) - 86400
        block_yesterday = Etherscan().get_block(yesterday)
        block_now = Etherscan().get_block(int(time.time()))
        tx_url = f"{self.url}&module=account&action=txlist&address={contract}&startblock={block_yesterday}&endblock={block_now}&page=1&offset=1000&sort=asc&apikey={self.key}"
        tx_response = requests.get(tx_url)
        tx_data = tx_response.json()
        if tx_data:
            tx_entry_count = len(tx_data["result"]) if "result" in tx_data else 0
        else:
            tx_entry_count = 0

        internal_tx_url = f"{self.url}&module=account&action=txlist&address={contract}&startblock={block_yesterday}&endblock={block_now}&page=1&offset=1000&sort=asc&apikey={self.key}"
        internal_tx_response = requests.get(internal_tx_url)
        internal_tx_data = internal_tx_response.json()
        if internal_tx_data:
            internal_tx_entry_count = (
                len(internal_tx_data["result"]) if "result" in internal_tx_data else 0
            )
        else:
            internal_tx_entry_count = 0
        entry_count = tx_entry_count + internal_tx_entry_count
        return entry_count

    def get_gas(self):
        url = f"{self.url}&module=gastracker&action=gasoracle&apikey={self.key}"
        response = requests.get(url)
        return response.json()

    def get_native_balance(self, wallet):
        url = f"{self.url}&module=account&action=balancemulti&address={wallet}&tag=latest&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        amount = int(data["result"][0]["balance"]) / 10**18
        if "e-" in str(amount):
            return "{:.8f}".format(amount)
        elif amount < 1:
            return "{:.8f}".format(amount)
        else:
            return "{:.2f}".format(amount)

    def get_native_price(self, token):
        url = f"{self.url}&module=stats&action={token}price&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return float(data["result"]["ethusd"])

    def get_token_balance(self, wallet, token, decimals):
        url = f"{self.url}&module=account&action=tokenbalance&contractaddress={token}&address={wallet}&tag=latest&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        if int(data["result"]):
            return int(data["result"][: -int(decimals)])
        else:
            return 0

    def get_verified(self, contract, chain):
        url = f"{self.url}&module=contract&action=getsourcecode&address={contract}&apikey={self.key}"
        response = requests.get(url)
        data = response.json()
        return True if "SourceCode" in data["result"][0] else False
