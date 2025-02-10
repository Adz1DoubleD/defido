import os
import requests

from bot import constants


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
            if data["data"] is not None:
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
                change = "1HR Change: N/A\n6HR Change: N/A\n24HR Change: N/A"
                return None, change
        else:
            change = "1HR Change: N/A\n6HR Change: N/A\n24HR Change: N/A"
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
