from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot import constants
import asyncio
import json
import os
import threading
import time
import websocket
from datetime import datetime

from hooks import api
from main import application

etherscan = api.Etherscan()


def sell(data):
    eth_price = etherscan.get_native_price(constants.CHAIN_NATIVE.lower())
    image = data["payload"]["payload"]["item"]["permalink"]
    price = int(data["payload"]["payload"]["sale_price"]) / 10**18
    price_usd = price * eth_price
    address = data["payload"]["payload"]["transaction"]["hash"]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        application.bot.send_message(
            constants.TELEGRAM_CHANNEL_ID,
            f"*{constants.NFT_NAME} Sale!*\n\n"
            f"{price} {constants.CHAIN_NATIVE.upper()} (${price_usd:.0f})\n\n"
            f"{image}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="View TX",
                            url=f"{constants.SCAN_ADDRESS}/tx/{address}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Opensea",
                            url=f"{image}",
                        )
                    ],
                ]
            ),
        )
    )


def listing(data):
    image = data["payload"]["payload"]["item"]["permalink"]
    expiration_date_str = data["payload"]["payload"]["expiration_date"]
    expiration_date = datetime.fromisoformat(expiration_date_str[:-6])
    current_date = time.time()
    time_difference = expiration_date - current_date
    days = time_difference.days
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        application.bot.send_message(
            constants.TELEGRAM_CHANNEL_ID,
            f"New *{constants.NFT_NAME} Listing!*\n\n"
            f"Listing Ends: {expiration_date}\n"
            f"({days} days, {hours} hours and {minutes} minutes)\n\n"
            f"{image}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Opensea",
                            url=f"{image}",
                        )
                    ],
                ]
            ),
        )
    )


def send(ws):
    global connection_attempts

    while True:
        try:
            ws.send(
                json.dumps(
                    {"topic": "phoenix", "event": "heartbeat", "payload": {}, "ref": 0}
                )
            )
            time.sleep(30)
        except Exception:
            connection_attempts += 1
            if connection_attempts >= 3:
                raise
            else:
                continue


def filter(ws, message):
    data = json.loads(message)
    event_type = data.get("event")
    if event_type == "item_sold":
        sell(data)
    else:
        return


def start(ws):
    global connection_attempts
    connection_attempts = 0

    try:
        ws.send(
            json.dumps(
                {
                    "topic": f"collection:{constants.NFT_SLUG}",
                    "event": "phx_join",
                    "payload": {},
                    "ref": 0,
                }
            )
        )
        threading.Thread(target=send, args=(ws,), daemon=True).start()
    except Exception:
        run()


def run():
    while True:
        try:
            ws = websocket.WebSocketApp(
                "wss://stream.openseabeta.com/socket/websocket"
                + f"?token={os.getenv('OPENSEA_API_KEY')}",
                on_message=filter,
            )
            ws.on_open = start
            ws.run_forever()
        except Exception:
            time.sleep(10)


if __name__ == "__main__":
    run()
