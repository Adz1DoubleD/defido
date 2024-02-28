from data import mappings
import requests
import os
from datetime import datetime, timedelta
import time as t
from data import mappings 
import random


def escape_markdown(text):
    characters_to_escape = ['*', '_', '`']
    for char in characters_to_escape:
        text = text.replace(char, '\\' + char)
    return text


def get_block(chain: str, time: "int") -> str:
    if chain not in mappings.chains_info:
        raise ValueError(f"Invalid chain: {chain}")
    chain_info = mappings.chains_info[chain]
    url = f"{chain_info.url}?module=block&action=getblocknobytime&timestamp={time}&closest=before{chain_info.key}"
    response = requests.get(url)
    data = response.json()
    return data["result"]


def get_cg_search(token):
    url = "https://api.coingecko.com/api/v3/search?query=" + token
    response = requests.get(url)
    return response.json()


def get_cg_mcap(token):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token}&vs_currencies=usd&include_market_cap=true"
    response = requests.get(url)
    data = response.json()
    return data[token]["usd_market_cap"]


def get_fact():
    response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
    quote = response.json()
    return quote["text"]


def get_gas(chain):
    if chain not in mappings.chains_info:
        raise ValueError(f"Invalid chain: {chain}")
    chain_info = mappings.chains_info[chain]
    url = f"{chain_info.url}?module=gastracker&action=gasoracle{chain_info.key}"
    response = requests.get(url)
    return response.json()


def get_quote():
    response = requests.get("https://type.fit/api/quotes")
    data = response.json()
    quote = random.choice(data)
    quote_text = quote["text"]
    quote_author = quote["author"]
    if quote_author.endswith(", type.fit"):
        quote_author = quote_author[:-10].strip()

    return f'`"{quote_text}"\n\n-{quote_author}`'


def get_today():
    now = datetime.now()
    url = f"http://history.muffinlabs.com/date/{now.month}/{now.day}"
    response = requests.get(url)
    return response.json()


def get_word(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    data = response.json()

    definition = None
    audio_url = None

    if data and isinstance(data, list):
        meanings = data[0].get("meanings", [])
        if meanings:
            for meaning in meanings:
                definitions = meaning.get("definitions", [])
                if definitions:
                    definition = definitions[0].get("definition")
                    break

        phonetics = data[0].get("phonetics", [])
        if phonetics:
            first_phonetic = phonetics[0]
            audio_url = first_phonetic.get("audio")

    return definition, audio_url


def get_token_supply_mcap_holders(pair, chain):
    if chain in mappings.dextools_chain:
        dextools_chain = mappings.dextools_chain[chain]
    url = f'http://public-api.dextools.io/trial/v2/token/{dextools_chain}/{pair}/info'
    headers = {
        'accept': 'application/json',
        'x-api-key': os.getenv("DEXTOOLS_API_KEY")
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data["data"]["totalSupply"], data["data"]["mcap"], data["data"]["holders"]
    else:
        return None


def get_price(token, chain):
    if chain in mappings.dextools_chain:
        dextools_chain = mappings.dextools_chain[chain]
    url = f'http://public-api.dextools.io/trial/v2/token/{dextools_chain}/{token}/price'
    headers = {
        'accept': 'application/json',
        'x-api-key': os.getenv("DEXTOOLS_API_KEY")
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        
        data = response.json()
        price = data['data']['price']
        if "e-" in str(price):
            return "{:.8f}".format(price)
        elif price < 1:
            return "{:.8f}".format(price) 
        else:
            return "{:.2f}".format(price)
    else:
        return None


def get_liquidity(pair, chain):
    if chain in mappings.dextools_chain:
        dextools_chain = mappings.dextools_chain[chain]
    url = f'http://public-api.dextools.io/trial/v2/pool/{dextools_chain}/{pair}/liquidity'
    headers = {
        'accept': 'application/json',
        'x-api-key': os.getenv("DEXTOOLS_API_KEY")
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data["data"]
    else:
        return None


def get_scan(token: str, chain: str) -> dict:
    chains = {"eth": 1, "bsc": 56, "arb": 42161, "opti": 10, "poly": 137, "base": 8453}
    chain_number = chains.get(chain)
    if not chain_number:
        raise ValueError(f"{chain} is not a valid chain")
    url = f"https://api.gopluslabs.io/api/v1/token_security/{chain_number}?contract_addresses={token}"
    response = requests.get(url)
    return response.json()["result"]


def get_liquidity_dex(pair, chain):
    if chain in mappings.dextools_chain:
        dextools_chain = mappings.dextools_chain[chain]
    url = f'http://public-api.dextools.io/trial/v2/pool/{dextools_chain}/{pair}'
    headers = {
        'accept': 'application/json',
        'x-api-key': os.getenv("DEXTOOLS_API_KEY")
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data["data"]["exchange"]["name"]
    else:
        return None
  
    
def get_volume(pair, chain):
    if chain in mappings.defined_chain:
        chain = mappings.defined_chain[chain]

    url = "https://graph.defined.fi/graphql"

    headers = {
        "content_type": "application/json",
        "x-api-key": os.getenv("DEFINED_API_KEY")
    }

    volume = f'''
        query {{
        getDetailedPairStats(pairAddress: "{pair}", networkId: {chain}, bucketCount: 1, tokenOfInterest: token1) {{
            stats_day1 {{
            statsUsd {{
                volume {{
                currentValue
                }}
            }}
            }}
        }}
        }}
        '''

    response = requests.post(url, headers=headers, json={"query": volume})
    data = response.json()
    try:
        current_value = data['data']['getDetailedPairStats']['stats_day1']['statsUsd']['volume']['currentValue']
    except Exception:
        current_value = 0
    return current_value


def get_price_change(address, chain):
    if chain in mappings.defined_chain:
        chain = mappings.defined_chain[chain]

    url = "https://graph.defined.fi/graphql"

    headers = {
        "content_type": "application/json",
        "x-api-key": os.getenv("DEFINED_API_KEY")
    }

    current_timestamp = int(datetime.now().timestamp()) - 300
    one_hour_ago_timestamp = int((datetime.now() - timedelta(hours=1)).timestamp())
    twenty_four_hours_ago_timestamp = int((datetime.now() - timedelta(hours=24)).timestamp())
    seven_days_ago_timestamp = int((datetime.now() - timedelta(days=7)).timestamp())

    pricechange = f"""query {{
        getTokenPrices(
            inputs: [
                {{ 
                    address: "{address}"
                    networkId: {chain}
                    timestamp: {current_timestamp}
                }}
                {{ 
                    address: "{address}"
                    networkId: {chain}
                    timestamp: {one_hour_ago_timestamp}
                }}
                {{ 
                    address: "{address}"
                    networkId: {chain}
                    timestamp: {twenty_four_hours_ago_timestamp}
                }}
                {{ 
                    address: "{address}"
                    networkId: {chain}
                    timestamp: {seven_days_ago_timestamp}
                }}
            ]
        ) {{
            priceUsd
        }}
    }}"""
    try:
        response = requests.post(url, headers=headers, json={"query": pricechange})
        data = response.json()

        current_price = data["data"]["getTokenPrices"][0]["priceUsd"]
        one_hour_ago_price = data["data"]["getTokenPrices"][1]["priceUsd"]
        twenty_four_hours_ago_price = data["data"]["getTokenPrices"][2]["priceUsd"]
        seven_days_ago_price = data["data"]["getTokenPrices"][3]["priceUsd"]

        one_hour_change = round(((current_price - one_hour_ago_price) / one_hour_ago_price) * 100, 2)
        twenty_four_hours_change = round(
            ((current_price - twenty_four_hours_ago_price) / twenty_four_hours_ago_price) * 100, 2)
        seven_days_change = round(((current_price - seven_days_ago_price) / seven_days_ago_price) * 100, 2)

        result = f"1H Change: {one_hour_change}%\n24H Change: {twenty_four_hours_change}%\n7D Change: {seven_days_change}%"
    except Exception:
        result = "1H Change: N/A\n24H Change: N/A\n7D Change: N/A"
    return result
    

def get_native_balance(wallet, chain):
    if chain not in mappings.chains_info:
        raise ValueError(f"Invalid chain: {chain}")
    chain_info = mappings.chains_info[chain]
    url = f"{chain_info.url}?module=account&action=balancemulti&address={wallet}&tag=latest{chain_info.key}"
    response = requests.get(url)
    data = response.json()
    amount =  int(data["result"][0]["balance"]) / 10 ** 18
    if "e-" in str(amount):
        return "{:.8f}".format(amount)
    elif amount < 1:
        return "{:.8f}".format(amount) 
    else:
        return "{:.2f}".format(amount)


def get_native_price(token):
    tokens_info = {
        "eth": {
            "url": "https://api.etherscan.io/api?module=stats&action=ethprice",
            "key": os.getenv("ETHER"),
            "field": "ethusd",
        },
        "bnb": {
            "url": "https://api.bscscan.com/api?module=stats&action=bnbprice",
            "key": os.getenv("BSC"),
            "field": "ethusd",
        },
        "matic": {
            "url": "https://api.polygonscan.com/api?module=stats&action=maticprice",
            "key": os.getenv("POLY"),
            "field": "maticusd",
        },
    }
    if token not in tokens_info:
        raise ValueError(f"Invalid token: {token}")
    url = f"{tokens_info[token]['url']}&{tokens_info[token]['key']}"
    response = requests.get(url)
    data = response.json()
    return float(data["result"][tokens_info[token]["field"]])


def get_daily_tx_count(contract: str, chain: str, ) -> int:
    if chain not in mappings.chains_info:
        raise ValueError(f"Invalid chain: {chain}")
    chain_info = mappings.chains_info[chain]
    yesterday = int(t.time()) - 86400
    block_yesterday = get_block(chain, yesterday)
    block_now = get_block(chain, int(t.time()))
    tx_url = f"{chain_info.url}?module=account&action=txlist&address={contract}&startblock={block_yesterday}&endblock={block_now}&page=1&offset=1000&sort=asc{chain_info.key}"
    tx_response = requests.get(tx_url)
    tx_data = tx_response.json()
    tx_entry_count = len(tx_data['result']) if 'result' in tx_data else 0
    internal_tx_url = f"{chain_info.url}?module=account&action=txlist&address={contract}&startblock={block_yesterday}&endblock={block_now}&page=1&offset=1000&sort=asc{chain_info.key}"
    internal_tx_response = requests.get(internal_tx_url)
    internal_tx_data = internal_tx_response.json()
    internal_tx_entry_count = len(internal_tx_data['result']) if 'result' in internal_tx_data else 0
    entry_count = tx_entry_count + internal_tx_entry_count
    return entry_count


def get_block(chain: str, time: "int") -> str:
    if chain not in mappings.chains_info:
        raise ValueError(f"Invalid chain: {chain}")
    chain_info = mappings.chains_info[chain]
    url = f"{chain_info.url}?module=block&action=getblocknobytime&timestamp={time}&closest=before{chain_info.key}"
    response = requests.get(url)
    data = response.json()
    return data["result"]


def get_token_balance(wallet, token, chain):
    if chain not in mappings.chains_info:
        raise ValueError(f"Invalid chain: {chain}")
    chain_info = mappings.chains_info[chain]
    url = f"{chain_info.url}?module=account&action=tokenbalance&contractaddress={token}&address={wallet}&tag=latest{chain_info.key}"
    response = requests.get(url)
    data = response.json()
    if int(data["result"]):
        return int(data["result"][:-18])
    else:
        return 0

