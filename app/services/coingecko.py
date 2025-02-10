import requests


class Coingecko:
    def __init__(self):
        self.url = "https://api.coingecko.com/api/v3/"

    def search(self, token):
        endpoint = f"search?query={token}"
        response = requests.get(self.url + endpoint)
        return response.json()

    def get_mcap(self, token):
        endpoint = f"simple/price?ids={token}&vs_currencies=usd&include_market_cap=true"
        response = requests.get(self.url + endpoint)
        data = response.json()
        return data[token]["usd_market_cap"]
