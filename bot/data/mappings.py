import os


class ChainInfo:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key


chains_info = {
    "eth": ChainInfo("https://api.etherscan.io/api", os.getenv("ETHER"),),
    "bsc": ChainInfo("https://api.bscscan.com/api", os.getenv("BSC")),
    "arb": ChainInfo("https://api.arbiscan.io/api", os.getenv("ARB")),
    "opti": ChainInfo("https://api-optimistic.etherscan.io/api", os.getenv("OPTI")),
    "poly": ChainInfo("https://api.polygonscan.com/api", os.getenv("POLY")),
    "base": ChainInfo("https://api.basescan.org/api", os.getenv("BASE")),
}


dextools_url = {
    'eth': 'https://www.dextools.io/app/en/ether/pair-explorer/',
    'bsc': 'https://www.dextools.io/app/en/bnb/pair-explorer/',
    'poly': 'https://www.dextools.io/app/en/polygon/pair-explorer/',
    'arb': 'https://www.dextools.io/app/en/arbitrum/pair-explorer/',
    'opti': 'https://www.dextools.io/app/en/optimism/pair-explorer/',
    'base': 'https://www.dextools.io/app/en/base/pair-explorer/'
}


dextools_chain = {
    "eth": "ether",
    "arb": "arbitrum",
    "poly": "polygon",
    "bsc": "bsc",
    "opti": "optimism",
    "base": "base",
}


defined_chain = {
    "eth": "1",
    "arb": "42161",
    "poly": "137",
    "bsc": "46",
    "opti": "10",
    "base": "8453",
}


gas = {
    "eth": "https://etherscan.io/gastracker",
    "bsc": "https://bscscan.com/gastracker",
    "poly": "https://polygonscan.com/gastracker",
    "arb": "https://etherscan.io/gastracker",
    "opti": "https://etherscan.io/gastracker",
    "base": "https://basescan.org/gastracker"
}


scan = {
    "eth": "https://etherscan.io/address",
    "bsc": "https://bscscan.com/address",
    "poly": "https://polygonscan.com/address",
    "arb": "https://etherscan.io/address",
    "opti": "https://etherscan.io/address",
    "base": "https://basescan.org/address"
}


native = {
    "eth": "eth",
    "bsc": "bnb",
    "poly": "matic",
    "arb": "eth",
    "opti": "eth",
    "base": "eth"
}

