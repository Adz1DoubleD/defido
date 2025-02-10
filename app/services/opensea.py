import os
import requests


class Opensea:
    def __init__(self):
        self.url = "https://api.opensea.io/api/v2/"
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
