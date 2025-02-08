import os, requests, time

from bot import constants


class CoinGecko:
    def __init__(self):
        self.url = f"https://api.coingecko.com/api/v3/"

    def search(self, token):
        endpoint = f"search?query={token}"
        response = requests.get(self.url + endpoint)
        return response.json()

    def get_mcap(self, token):
        endpoint = f"simple/price?ids={token}&vs_currencies=usd&include_market_cap=true"
        response = requests.get(self.url + endpoint)
        data = response.json()
        return data[token]["usd_market_cap"]


class Dextools:
    def __init__(self):
        self.plan = "trial"
        self.headers = {
            "accept": "application/json",
            "x-api-key": os.getenv("DEXTOOLS_API_KEY"),
        }
        self.url = f"http://public-api.dextools.io/{self.plan}/v2/"

    def get_token_info(self, pair):
        endpoint = f"token/{constants.CHAIN}/{pair.lower()}/info"
        response = requests.get(self.url + endpoint, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            if data and "data" in data and data["data"]:
                mcap = data["data"].get("mcap", 0)
                holders = data["data"].get("holders", 0)

                return {"mcap": mcap, "holders": holders}
            else:
                return {"mcap": None, "holders": None}
        else:
            return {"mcap": None, "holders": None}

    def get_price(self, token):
        endpoint = f"token/{constants.CHAIN}/{token.lower()}/price"
        response = requests.get(self.url + endpoint, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            if data["data"] != None:
                price = data["data"]["price"]
                if "e-" in str(price):
                    price = "{:.8f}".format(price)
                elif price < 1:
                    price = "{:.8f}".format(price)
                else:
                    price = "{:.2f}".format(price)

                one_hour = data["data"].get("variation1h", None)
                six_hour = data["data"].get("variation6h", None)
                one_day = data["data"].get("variation24h", None)

                if one_hour is not None:
                    one_hour = f"1HR Change: {round(one_hour, 2)}%"
                else:
                    one_hour = "1HR Change: N/A"

                if six_hour is not None:
                    six_hour = f"6HR Change: {round(six_hour, 2)}%"
                else:
                    six_hour = "6HR Change: N/A"

                if one_day is not None:
                    one_day = f"24HR Change:  {round(one_day, 2)}%"
                else:
                    one_day = "24HR Change: N/A"

                change = f"{one_hour}\n{six_hour}\n{one_day}"

                return price, change
            else:
                change = f"1HR Change: N/A\n6HR Change: N/A\n24HR Change: N/A"
                return None, change
        else:
            change = f"1HR Change: N/A\n6HR Change: N/A\n24HR Change: N/A"
            return None, change

    def get_liquidity(self, pair):

        if isinstance(pair, list):
            total_liquidity = {"mainToken": 0, "sideToken": 0, "liquidity": 0}

            for single_pair in pair:
                endpoint = f"pool/{constants.CHAIN}/{single_pair.lower()}/liquidity"
                response = requests.get(self.url + endpoint, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()
                    if "reserves" in data.get("data", {}):
                        reserves = data["data"]["reserves"]
                        total_liquidity["mainToken"] += float(
                            reserves.get("mainToken", 0)
                        )
                        total_liquidity["sideToken"] += float(
                            reserves.get("sideToken", 0)
                        )
                        total_liquidity["liquidity"] += float(
                            data.get("data", {}).get("liquidity", 0)
                        )
                else:
                    pass

            return total_liquidity
        else:
            endpoint = f"pool/{constants.CHAIN}/{pair.lower()}/liquidity"
            response = requests.get(self.url + endpoint, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                if "reserves" in data.get("data", {}):
                    reserves = data["data"]["reserves"]
                    main_token = float(reserves.get("mainToken", 0))
                    side_token = float(reserves.get("sideToken", 0))
                    liquidity = float(data.get("data", {}).get("liquidity", 0))

                    return {
                        "mainToken": main_token,
                        "sideToken": side_token,
                        "liquidity": liquidity,
                    }
            else:
                return None

    def get_dex(self, pair):
        if isinstance(pair, list):
            dex_names = []
            for single_pair in pair:
                endpoint = f"pool/{constants.CHAIN}/{single_pair.lower()}"
                response = requests.get(self.url + endpoint, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()
                    dex_name = data.get("data", {}).get("exchange", {}).get("name")
                    dex_names.append(dex_name)
                else:
                    dex_names.append(None)

            return dex_names
        else:
            endpoint = f"pool/{constants.CHAIN}/{pair.lower()}"
            response = requests.get(self.url + endpoint, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("exchange", {}).get("name")
            else:
                return "Unknown"

    def get_volume(self, pair):
        if isinstance(pair, list):
            total_volume = 0
            for single_pair in pair:

                endpoint = f"pool/{constants.CHAIN}/{single_pair.lower()}/price"
                response = requests.get(self.url + endpoint, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    try:
                        current_value = data["data"]["volume24h"]
                        total_volume += current_value
                    except Exception:
                        pass
                else:
                    return 0
            return total_volume

        else:
            endpoint = f"pool/{constants.CHAIN}/{pair.lower()}/price"
            response = requests.get(self.url + endpoint, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                try:
                    current_value = data["data"]["volume24h"]
                except Exception:
                    current_value = 0
                return current_value
            else:
                return 0


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


class Opensea:
    def __init__(self):
        self.url = f"https://api.opensea.io/api/v2/"
        self.headers = {"X-API-KEY": os.getenv("OPENSEA_API_KEY")}

    def get_collection(self, slug):
        endpoint = f"collections/{slug}"
        response = requests.get(self.url + endpoint, headers=self.headers)
        data = response.json()
        return data

    def get_nft_id(self, nft, id, chain):
        endpoint = f"chain/{chain}/contract/{nft}/nfts/{id}"

        response = requests.get(self.url + endpoint, headers=self.headers)
        data = response.json()
        return data

    def get_collection_stats(self, slug):
        endpoint = f"collections/{slug}/stats"

        response = requests.get(self.url + endpoint, headers=self.headers)
        data = response.json()
        return data
