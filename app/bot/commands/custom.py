from telegram import Update
from telegram.ext import ContextTypes

from bot import constants
from utils import tools
from services import get_dextools

dextools = get_dextools()


BRIDGE_TEXT = (
    "*BASE Bridges*\n\n"
    "- [Official Base Bridge](https://bridge.base.org/deposit)\n"
    "- [HoudiniSwap](http://www.houdiniswap.com/)\n"
    "- [Synapse Protocol](https://synapseprotocol.com/?fromChainId=1&toChainId=8453)\n"
    "- [Orbiter Finance](https://www.orbiter.finance/?source=Ethereum&dest=Base&token=ETH)\n"
    "- [Rhino (BSC ETH to BASE)](https://app.rhino.fi/bridge?token=ETH&chainOut=BASE&chain=BINANCE)"
)


RPC_TEXT = (
    "*Add BASE to Metamask:*\n\n"
    "Use the following link and click 'Connect Wallet', Followed by 'Add to Metamask' - "
    "https://chainlist.org/?search=base\n\n"
    "Or to add manually:\n"
    "Open MetaMask, Select 'Add Network' from the 'Network' dropdown menu and enter the following infomation into 'Custom Networks' on mobile or 'Add a network manually' on PC:\n\n"
    "- Network Name: `Base Mainnet`\n"
    "- Description (mobile only): `Base Mainnet` \n"
    "- RPC URL: `https://mainnet.base.org`\n"
    "- Chain ID: `8453`\n"
    "- Currency Symbol: `ETH`\n"
    "- Block Explorer: `https://basescan.org`"
)


async def bridge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Guides*\n\n{BRIDGE_TEXT}",
        parse_mode="Markdown",
    )


async def guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Guides*\n\n{RPC_TEXT}\n\n{BRIDGE_TEXT}",
        parse_mode="Markdown",
    )


async def rpc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Guides*\n\n{RPC_TEXT}",
        parse_mode="Markdown",
    )


async def tweet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Tweet\n\nhttps://x.com/coinbase/status/1437511766510956545",
        parse_mode="Markdown",
    )


HANDLERS = [
    (func.__name__.split("_")[0], func, description)
    for func, description in [
        (bridge, "Bridge links"),
        (guide, "FAQs"),
        (rpc, "RPC info"),
        (tweet, "Tweet"),
    ]
]
