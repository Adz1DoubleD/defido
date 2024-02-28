
from telegram import *
from telegram.ext import *

from data import constants, db, api, mappings
import os
from media import index as media

import locale
locale.setlocale(locale.LC_ALL, '')


async def ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA  == "None":
        await update.message.reply_photo(
        photo = media.logo(),
        caption=
            f"*{constants.PROJECT_NAME} CA*\n\nComing Soon!\n\n",
        parse_mode="Markdown"
        )
        return

    await update.message.reply_photo(
        photo = media.logo(),
        caption=
            f"*{constants.PROJECT_NAME} CA* \n\n`{constants.CA}`\n\n",
        parse_mode="Markdown"
    )


async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA  == "None":
        await update.message.reply_photo(
        photo = media.logo(),
        caption =
            f"*{constants.PROJECT_NAME} CA*\n\nComing Soon!\n\n",
        parse_mode="Markdown"
        )
        return
    await update.message.reply_photo(
        photo = media.logo(),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{constants.PROJECT_NAME} Chart", url=f"{constants.DEXTOOLS}{constants.CA}"
                    )
                ]
            ]
        ),
    )


async def compare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if constants.CA  == "None":
            await update.message.reply_photo(
            photo = media.logo(),
            caption =
                f"*{constants.PROJECT_NAME} Compare*\n\nComing Soon!\n\n",
            parse_mode="Markdown"
            )
            return
        if len(context.args) == 1:
            token2 = context.args[0].lower()
            search = api.get_cg_search(token2)
            token_id = search["coins"][0]["api_symbol"]
            token_mcap = api.get_cg_mcap(token_id)
            if token_mcap == 0:
                await update.message.reply_photo(
                    photo = media.logo(),
                    caption = f"*{constants.PROJECT_NAME} Market Cap Comparison*\n\n"
                    f"No Market Cap data found for {token2.upper()}",
                    parse_mode="Markdown",
                )

            else:
                supply,mcap,_ = api.get_token_supply_mcap_holders(ca, constants.CHAIN)
                if not mcap:
                    mcap = float(api.get_price(ca, constants.CHAIN)) * float(supply)
                percent = ((token_mcap - mcap) / mcap) * 100
                x = (token_mcap - mcap) / mcap
                token_value = token_mcap / supply
                await update.message.reply_photo(
                    photo = media.logo(),
                    caption = f"*{constants.PROJECT_NAME} Market Cap Comparison*\n\n"
                    f"{context.args[0].upper()} Market Cap:\n"
                    f'${"{:,.2f}".format(token_mcap)}\n\n'
                    f"Token value of {constants.PROJECT_NAME} at {context.args[0].upper()} Market Cap:\n"
                    f'${"{:,.2f}".format(token_value)}\n'
                    f'{"{:,.0f}%".format(percent)}\n'
                    f'{"{:,.0f}x".format(x)}',
                    parse_mode="Markdown",
                )
        else:     
            await update.message.reply_photo(
                    photo = media.logo(),
                    caption = "Please follow the command with the name of the tokn you want to compare with",
                )
    except Exception:
        await update.message.reply_text("Comparison not avaliable, please try again.")


async def holders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA  == "None":
        await update.message.reply_photo(
        photo = media.logo(),
        caption=
            f"*{constants.PROJECT_NAME} Holders*\n\nComing Soon!\n\n",
        parse_mode="Markdown"
        )
        return

    _,_,holders = api.get_token_supply_mcap_holders(constants.CA, constants.CHAIN)
    await update.message.reply_photo(
        photo = media.logo(),
        caption = 
            f"*{constants.PROJECT_NAME} Holders*\n\n"
            f"{holders}\n\n",
        parse_mode="Markdown"
        )


async def liquidity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA  == "None":
        await update.message.reply_photo(
        photo= media.logo(),
        caption =
            f"*{constants.PROJECT_NAME} Liquidity*\n\nComing Soon!\n\n",
        parse_mode="Markdown"
        )
        return

    liquidity_data = api.get_liquidity(constants.PAIR, constants.CHAIN)
    token_liq = float(liquidity_data["reserves"]["mainToken"])
    weth_liq = float(liquidity_data["reserves"]["sideToken"])
    liq = liquidity_data["liquidity"]
    dex = api.get_liquidity_dex(constants.PAIR, constants.CHAIN)
    scan = api.get_scan(constants.CA, constants.CHAIN)
    if scan[f"{str(constants.CA).lower()}"]["is_in_dex"] == "1":
        token_address_str = str(constants.CA)
        if "lp_holders" in scan[token_address_str]:
            locked_lp_list = [
                lp
                for lp in scan[token_address_str]["lp_holders"]
                if lp["is_locked"] == 1
                and lp["address"]
                != "0x0000000000000000000000000000000000000000"
            ]
            lock = ""
            if locked_lp_list:
                lp_with_locked_detail = [
                    lp for lp in locked_lp_list if "locked_detail" in lp
                ]
                if lp_with_locked_detail:
                    percent = float(locked_lp_list[0]['percent'])
                    lock = (
                        f"Liquidity Locked - {locked_lp_list[0]['tag']} - {percent * 100:.2f}%\n"
                        f"Unlock - {locked_lp_list[0]['locked_detail'][0]['end_time'][:10]}"
                    )
                else:
                    percent = float(locked_lp_list[0]['percent'])
                    lock = f"Liquidity Locked - {percent * 100:.2f}%"
    else:
        lock = ""
    lock_caption = f'\n\n{lock}' if lock else ''
    formatted_token_liq = locale.format_string("%.0f", token_liq, grouping=True)

    if token_liq >= 1_000_000:
        formatted_token_liq = f'{token_liq / 1_000_000:.1f}M'

    await update.message.reply_photo(
        photo = media.logo(),
        caption = f"*{constants.PROJECT_NAME} Liquidity*\n\n"
                f"{dex} pair\n"
                f'{formatted_token_liq} {constants.PROJECT_NAME.upper()}\n\n'
                f'{weth_liq:.5f} WETH\n\n'
                f'Total Liquidity ${"{:0,.0f}".format(liq)}{lock_caption}\n\n',
        parse_mode="Markdown"
        )


async def mcap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA  == "None":
        await update.message.reply_photo(
        photo = media.logo(),
        caption =
            f"*{constants.PROJECT_NAME} Market Cap*\n\nComing Soon!\n\n",
        parse_mode="Markdown"
        )
        return
    price = api.get_price(constants.CA, constants.CHAIN)
    supply, mcap,_ = api.get_token_supply_mcap_holders(constants.CA, constants.CHAIN)
    if not mcap:
        mcap = float(price) * float(supply)
    formatted_mcap = "${:,.0f}".format(mcap)
    await update.message.reply_photo(
        photo = media.logo(),
        caption=
            f"*{constants.PROJECT_NAME} Market Cap*\n\n"
            f"{formatted_mcap}\n\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Chart", url=f"{constants.DEXTOOLS}{constants.PAIR}"
                    )
                ],
            ]
        ),
    )


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA  == "None":
        await update.message.reply_photo(
        photo = media.logo(),
        caption =
            f"*{constants.PROJECT_NAME} Price*\n\nComing Soon!\n\n",
        parse_mode="Markdown"
        )
        return
    supply, mcap, holders = api.get_token_supply_mcap_holders(constants.CA, constants.CHAIN)
    price = api.get_price(constants.CA, constants.CHAIN)
    volume = "${:,.0f}".format(float(api.get_volume(constants.PAIR, constants.CHAIN)))

    if not mcap:
        mcap = float(price) * float(supply)

    formatted_mcap = "${:,.0f}".format(mcap)

    price_change = api.get_price_change(constants.CA, constants.CHAIN)
    await update.message.reply_photo(
        photo = media.logo(),
        caption =
            f"*{constants.PROJECT_NAME} Token Info*\n\n"
            f'Price: {price}\n'
            f"Market Cap: {formatted_mcap}\n"
            f"24 Hour Volume: {volume}\n"
            f"Holders: {holders}\n\n"
            f"{price_change}\n\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Chart", url=f"{constants.DEXTOOLS}{constants.PAIR}"
                    )
                ],
            ]
        ),
    )


async def tax(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA  == "None":
        await update.message.reply_photo(
        photo = media.logo(),
        caption =
            f"*{constants.PROJECT_NAME} Tax*\n\nComing Soon!\n\n",
        parse_mode="Markdown"
        )
        return
    scan = api.get_scan(constants.CA, constants.CHAIN)
    buy_tax_raw = (
        float(scan[f"{str(ca).lower()}"]["buy_tax"]) * 100
    )
    sell_tax_raw = (
        float(scan[f"{str(ca).lower()}"]["sell_tax"]) * 100
    )
    buy_tax = int(buy_tax_raw)
    sell_tax = int(sell_tax_raw)
    tax = f"*{constants.PROJECT_NAME} Tax*\n\n{buy_tax}/{sell_tax}"
    await update.message.reply_photo(
        photo = media.logo(),
        caption =
            f'{tax}\n\n',
        parse_mode="Markdown",)
    

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) >= 1:
        if constants.CA  == "None":
            await update.message.reply_photo(
            photo = media.logo(),
            caption =
                f"*{constants.PROJECT_NAME} Wallet Info*\n\nComing Soon!\n\n",
            parse_mode="Markdown"
            )
            return
    else:
        await update.message.reply_text(
        f"Please use /wallet [wallet_address]")
        return
    if not wallet.startswith("0x"):
        await update.message.reply_text(
        f"Please use /wallet [wallet_address]")
        return
    native_price = api.get_native_price(constants.CHAIN_NATIVE)
    eth = api.get_native_balance(wallet, constants.CHAIN)
    eth_dollar = float(eth) * float(native_price)
    balance = api.get_token_balance(wallet, ca, constants.CHAIN)
    price = api.get_price(ca, constants.CHAIN)
    token_dollar = float(balance) * float(price)
    supply,_,_ = api.get_token_supply_mcap_holders(constants.CA, constants.CHAIN)
    percent = round(balance / supply * 100, 2)
    txs = api.get_daily_tx_count(wallet, constants.CHAIN)
    percent = round(balance / supply * 100, 2)
    await update.message.reply_photo(
        photo = media.logo(),
        caption =
            f"*{constants.PROJECT_NAME} Wallet Info*\n\n"
            f"`{wallet}`\n\n"
            f"{eth} {constants.CHAIN_NATIVE.upper()} (${'{:0,.0f}'.format(eth_dollar)})\n"
            f"{balance} {constants.PROJECT_NAME} {percent}% (${'{:0,.0f}'.format(token_dollar)})\n\n"
            f"{txs} tx's in the last 24 hours\n\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Wallet Link",
                        url=f"{constants.SCAN}{wallet}",
                    )
                ],
            ]
        ),
    )



async def filters_list(update: Update, context: CallbackContext) -> None:
    words = db.filters_get()

    if words:
        await update.message.reply_text(f"{constants.PROJECT_NAME} custom filters:\n\n{words}")
    else:
        await update.message.reply_text("The filters list is empty.")


async def leaderboard(update: Update, context: CallbackContext):
    board = db.clicks_get_leaderboard()
    click_counts_total = db.clicks_get_total()
    fastest = db.clicks_fastest_time()
    fastest_user = fastest[0]
    fastest_time = fastest[1]
    slowest = db.clicks_slowest_time()
    slowest_user = slowest[0]
    slowest_time = slowest[1]
    await update.message.reply_text(
        text=f"*{constants.PROJECT_NAME} Leaderboard\n(Top 10)\n\n*"
            f"{api.escape_markdown(board)}\n"
            f"Total clicks: *{click_counts_total}*\n\n"
            f"Fastest click:\n{fastest_time} seconds\nby {api.escape_markdown(fastest_user)}\n\n"
            f"Slowest click:\n{slowest_time} seconds\nby {api.escape_markdown(slowest_user)}\n\n"
        ,parse_mode="Markdown"
    )


async def me(update: Update, context: CallbackContext):
    user = update.effective_user
    user_info = user.username or f"{user.first_name} {user.last_name}"
    user_data = db.clicks_get_by_name(user_info)
    clicks = user_data[0]
    fastest_time = user_data[1]

    if fastest_time is None:
        message = f"*{constants.PROJECT_NAME} Leaderboard*\n\n" \
                  f"{api.escape_markdown(user_info)}, You have been the fastest clicker *{clicks}* times\n\n" \
                  f"Your fastest time has not been logged yet"
    else:
        message = f"*{constants.PROJECT_NAME} Leaderboard*\n\n" \
                  f"{api.escape_markdown(user_info)}, You have been the fastest clicker *{clicks}* times\n\n" \
                  f"Your fastest time is {fastest_time} seconds\n\n"

    await update.message.reply_text(
        text=message,
        parse_mode="Markdown"
    )


async def twitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=media.logo(),
        reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=f"{constants.TWITTER}",
                                url=f"https://{constants.TWITTER}",
                            )
                        ],
                    ]
                ),
            )


async def website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=media.logo(),
        reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=f"{constants.WEBSITE}",
                                url=f"https://{constants.WEBSITE}",
                            )
                        ],
                    ]
                ),
            )


