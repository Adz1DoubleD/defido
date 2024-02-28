from datetime import datetime
import random

PROJECT_NAME = "DeFido"
TWITTER = "twitter.com/defidotoken"
WEBSITE = "linktr.ee/defidotoken"
DEXTOOLS = "https://dextools.io/app/en/base/pair-explorer/"
CA = "None"
PAIR = "None"
CHAIN = "base"
CHAIN_NATIVE = "ETH"
SCAN_ADDRESS = "https://basescan.org/address/"
TELEGRAM_CHANNEL_ID = '-1001998745415'

ADMINS = [762713289, 1866802617, 1667971437]

def RANDOM_BUTTON_TIME():
    time = random.randint(3600, 21600)
    return time

FIRST_BUTTON_TIME = RANDOM_BUTTON_TIME()
BUTTON_TIME = None
RESTART_TIME = datetime.now().timestamp()

