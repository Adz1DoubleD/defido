from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from datetime import datetime, timedelta

from bot import constants
from hooks import api, tools
from media import images


coingecko = api.CoinGecko()
dextools = api.Dextools()
etherscan = api.Etherscan()
opensea = api.Opensea()


async def burn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA == "None":
        await update.message.reply_photo(
            photo=tools.get_logo(),
            caption=f"*{constants.PROJECT_NAME} CA*\n\nComing Soon!\n\n",
            parse_mode="Markdown",
        )
        return

    burn = etherscan.get_token_balance(constants.DEAD, constants.CA, constants.DECIMALS)
    percent = round(burn / constants.SUPPLY * 100, 2)
    price, _ = dextools.get_price(constants.CA)
    if price:
        price = price
    else:
        price = 0
    burn_dollar = float(price) * burn
    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Burn Wallet* \n\n"
        f"{'{:0,.0f}'.format(float(burn))} (${'{:0,.0f}'.format(float(burn_dollar))})\n"
        f"{percent}% of Supply\n\n",
        parse_mode="markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Burn Wallet",
                        url=f"{constants.SCAN_ADDRESS}/token/{constants.CA}?a={constants.DEAD}",
                    )
                ],
            ]
        ),
    )


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA == "None":
        await update.message.reply_photo(
            photo=tools.get_logo(),
            caption=f"*{constants.PROJECT_NAME} CA*\n\nComing Soon!\n\n",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_photo(
        photo=tools.get_logo(),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Buy On Uniswap",
                        url=f"https://app.uniswap.org/#/swap?chain={constants.CHAIN}&outputCurrency={constants.CA}",
                    )
                ]
            ]
        ),
    )


async def ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA == "None":
        await update.message.reply_photo(
            photo=tools.get_logo(),
            caption=f"*{constants.PROJECT_NAME} CA*\n\nComing Soon!\n\n",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} CA* \n\n`{constants.CA}`\n\n",
        parse_mode="Markdown",
    )


async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA == "None":
        await update.message.reply_photo(
            photo=tools.get_logo(),
            caption=f"*{constants.PROJECT_NAME} Chart*\n\nComing Soon!\n\n",
            parse_mode="Markdown",
        )
        return
    await update.message.reply_photo(
        photo=tools.get_logo(),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="📈 Chart", url=f"{constants.CHART_LINK}{constants.CA}"
                    )
                ]
            ]
        ),
    )


async def compare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if constants.CA == "None":
            await update.message.reply_photo(
                photo=tools.get_logo(),
                caption=f"*{constants.PROJECT_NAME} Compare*\n\nComing Soon!\n\n",
                parse_mode="Markdown",
            )
            return
        if len(context.args) == 1:
            token2 = context.args[0].lower()
            search = coingecko.search(token2)
            token_id = search["coins"][0]["api_symbol"]
            token_mcap = coingecko.get_mcap(token_id)
            if token_mcap == 0:
                await update.message.reply_photo(
                    photo=tools.get_logo(),
                    caption=f"*{constants.PROJECT_NAME} Market Cap Comparison*\n\n"
                    f"No Market Cap data found for {token2.upper()}",
                    parse_mode="Markdown",
                )

            else:
                info = dextools.get_token_info(constants.CA)
                mcap = info["mcap"]
                percent = ((token_mcap - mcap) / mcap) * 100
                x = (token_mcap - mcap) / mcap
                token_value = token_mcap / constants.SUPPLY
                await update.message.reply_photo(
                    photo=tools.get_logo(),
                    caption=f"*{constants.PROJECT_NAME} Market Cap Comparison*\n\n"
                    f"{context.args[0].upper()} Market Cap:\n"
                    f"${'{:,.2f}'.format(token_mcap)}\n\n"
                    f"Token value of {constants.TICKER} at {context.args[0].upper()} Market Cap:\n"
                    f"${'{:,.2f}'.format(token_value)}\n"
                    f"{'{:,.0f}%'.format(percent)}\n"
                    f"{'{:,.0f}x'.format(x)}",
                    parse_mode="Markdown",
                )
        else:
            await update.message.reply_photo(
                photo=tools.get_logo(),
                caption="Please follow the command with the name of the token you want to compare with",
            )
    except Exception:
        await update.message.reply_text("Comparison not avaliable, please try again.")


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Contact*\n\n{constants.EMAIL}",
        parse_mode="Markdown",
    )


async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        amount = " ".join(context.args)
        amount = amount.replace(",", "")
        if not amount.isdigit():
            await update.message.reply_text(
                f"Please provide a valid amount of {constants.TICKER} to convert"
            )
            return
        if int(amount) > constants.SUPPLY:
            await update.message.reply_text(
                f"{constants.TICKER} supply is {constants.SUPPLY}"
            )
            return
    else:
        await update.message.reply_text(
            f"Please follow the command with the amount of {constants.TICKER} you wish to convert"
        )
        return

    price, _ = dextools.get_price(constants.CA, constants.CHAIN)
    if price:
        price = price
    else:
        price = 0
    value = float(price) * float(amount)
    if value < 1:
        output = "{:0,.4f}".format(value)
    else:
        output = "{:0,.0f}".format(value)
    amount_str = float(amount)

    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"{amount_str:,.0f} {constants.TICKER} is currently worth:\n\n${output}\n\n",
        parse_mode="Markdown",
    )


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=(
            f"*{constants.PROJECT_NAME} Daily Tasks*\n\n"
            "Vote for us on the following links\n"
            f"- [Dexscreener](https://dexscreener.com/{constants.CHAIN}/{constants.CA})\n"
            f"- [Dextools](https://www.dextools.io/app/en/{constants.CHAIN}/pair-explorer/{constants.CA})\n"
            f"- [CoinGecko](https://www.coingecko.com/en/coins/{constants.TICKER.lower()})\n"
            f"- [Coin Market Cap](https://coinmarketcap.com/currencies/{constants.PROJECT_NAME})\n\n"
            "Like and RT everything on the link below\n"
            f"- [{constants.PROJECT_NAME} Twitter Search](https://twitter.com/search?q=%23{constants.PROJECT_NAME.upper()}&src=typed_query)\n\n"
            f"Post at least 5 tweets a day and share them here with the link below\n"
            f"- [Create Tweets with {constants.PROJECT_NAME} tags](http://twitter.com/intent/tweet?text=%0A%0A%0A@{constants.TWITTER}%20${constants.PROJECT_NAME.upper()}&url=%0A{constants.WEBSITE}&hashtags={constants.PROJECT_NAME.upper()}%2CDEFIDOGS)"
        ),
        parse_mode="Markdown",
    )


async def discord(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=images.discord,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Discord",
                        url=f"https://{constants.DISCORD}",
                    )
                ],
            ]
        ),
    )


async def holders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA == "None":
        await update.message.reply_photo(
            photo=tools.get_logo(),
            caption=f"*{constants.PROJECT_NAME} Holders*\n\nComing Soon!\n\n",
            parse_mode="Markdown",
        )
        return

    info = dextools.get_token_info(constants.CA)
    holders = info["holders"]
    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Holders*\n\n{holders}\n\n",
        parse_mode="Markdown",
    )


async def launch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    duration = constants.LAUNCH - datetime.utcnow()
    days, hours, minutes = tools.duration_days(abs(duration))
    footer = "ago" if duration < timedelta(0) else "to go"
    await update.message.reply_photo(
        photo=images.launch,
        caption=(
            f"*DeFido Launch*\n\n"
            f"{constants.LAUNCH.strftime('%A %B %d %Y %I:%M %p')} UTC\n\n"
            f"{days} days, {hours} hours and {minutes} minutes {footer}"
        ),
        parse_mode="Markdown",
    )


async def liquidity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA == "None":
        await update.message.reply_photo(
            photo=tools.get_logo(),
            caption=f"*{constants.PROJECT_NAME} Liquidity*\n\nComing Soon!\n\n",
            parse_mode="Markdown",
        )
        return

    liq_text = ""
    buttons = []
    liq = 0
    total_token = 0
    total_eth = 0

    if isinstance(constants.PAIR, list):
        for pair in constants.PAIR:
            liquidity_data = dextools.get_liquidity(pair)
            token_liq = float(liquidity_data["mainToken"])
            weth_liq = float(liquidity_data["sideToken"])
            liq += liquidity_data["liquidity"]
            total_token += token_liq
            total_eth += weth_liq
            dex = dextools.get_dex(pair)

            liq_text += (
                f"{dex} pair\n"
                f"{token_liq:,.0f} {constants.TICKER.upper()}\n"
                f"{weth_liq:.2f} {constants.CHAIN_NATIVE.upper()}\n\n"
            )

            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{dex}", url=f"{constants.SCAN_ADDRESS}/address/{pair}"
                    )
                ]
            )

        total_liquidity_info = (
            f"Total Liquidity\n"
            f"{total_token:,.0f} {constants.TICKER}\n"
            f"{total_eth:.2f} {constants.CHAIN_NATIVE}\n"
        )

    else:
        liquidity_data = dextools.get_liquidity(constants.PAIR)
        token_liq = float(liquidity_data["mainToken"])
        weth_liq = float(liquidity_data["sideToken"])
        liq = liquidity_data["liquidity"]

        dex = dextools.get_dex(constants.PAIR)
        liq_text += (
            f"{dex} pair\n"
            f"{token_liq:,.0f} {constants.TICKER.upper()}\n"
            f"{weth_liq:.5f} {constants.CHAIN_NATIVE.upper()}\n\n"
        )

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{dex}",
                    url=f"{constants.SCAN_ADDRESS}/address/{constants.PAIR}",
                )
            ]
        )

        total_liquidity_info = "Total Liquidity\n"

    buttons.append([InlineKeyboardButton(text="Lock TX", url=f"{constants.LOCK_TX}")])

    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Liquidity*\n\n"
        f"Total Supply: {constants.SUPPLY:,.0f}\n\n"
        f"{liq_text}"
        f"{total_liquidity_info}"
        f"${'{:0,.0f}'.format(liq)}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def mcap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA == "None":
        await update.message.reply_photo(
            photo=tools.get_logo(),
            caption=f"*{constants.PROJECT_NAME} Market Cap*\n\nComing Soon!\n\n",
            parse_mode="Markdown",
        )
        return
    info = dextools.get_token_info(constants.CA)
    mcap = info["mcap"]
    if mcap:
        formatted_mcap = "${:,.0f}".format(mcap)
    else:
        formatted_mcap = "N/A"
    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Market Cap*\n\n{formatted_mcap}\n\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Chart", url=f"{constants.CHART_LINK}{constants.CA}"
                    )
                ],
            ]
        ),
    )


async def media_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.MEDIA_LINK == "None":
        return

    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Media*\n\n{constants.MEDIA_LINK}",
        parse_mode="Markdown",
    )


async def nft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id = " ".join(context.args)
    data = opensea.get_collection(constants.NFT_SLUG)
    minted = data["total_supply"]
    if id == "":
        stats = opensea.get_collection_stats(constants.NFT_SLUG)
        price = etherscan.get_native_price(constants.CHAIN_NATIVE.lower())
        owners = stats["total"]["num_owners"]

        floor = stats["total"]["floor_price"]
        floor_dollar = floor * price
        volume = stats["total"]["volume"]
        sales = stats["total"]["sales"]
        avg_price = stats["total"]["average_price"]

        caption_text = (
            f"*{constants.NFT_NAME}*\n\nOwners: {owners}\nSupply: {constants.NFT_SUPPLY}\n\n"
            f"Floor Price: {floor:,.4f} {constants.CHAIN_NATIVE.upper()} (${floor_dollar:,.0f})"
        )

        if avg_price != 0.0:
            avg_price_dollar = avg_price * price
            caption_text += f"\nAverage Price: {avg_price:.2f} {constants.CHAIN_NATIVE.upper()} (${avg_price_dollar:,.0f})"

        if volume != 0.0:
            volume_dollar = volume * price
            caption_text += f"\nVolume: {volume:.2f} {constants.CHAIN_NATIVE.upper()} (${volume_dollar:,.0f})"

        if sales != 0.0:
            caption_text += f"\nSales: {sales}"

        await update.message.reply_photo(
            photo=images.nft,
            caption=caption_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Rarible",
                            url=f"https://rarible.com/collection/{constants.CHAIN}/{constants.NFT_ADDRESS}/items",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Opensea",
                            url=f"https://opensea.io/collection/{constants.NFT_SLUG}",
                        )
                    ],
                ]
            ),
        )
    else:
        data = opensea.get_nft_id(constants.NFT_ADDRESS, id, constants.CHAIN)
        if "nft" in data and data["nft"]:
            traits = data["nft"]["traits"]
            url = data["nft"]["opensea_url"]
            rank = data["nft"]["rarity"]["rank"]
            formatted_traits = "\n".join(
                [f"{trait['trait_type']}: {trait['value']}" for trait in traits]
            )

        else:
            await update.message.reply_text(f"NFT {id} not found")
            return

        await update.message.reply_text(
            f"*{constants.NFT_NAME} #{id}*\n\nRarity Rank: {rank}/{minted}\n{formatted_traits}\n\n{url}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"Rarible {constants.NFT_NAME} #{id}",
                            url=f"https://rarible.com/collection/{constants.CHAIN}/{constants.NFT_ADDRESS}:{id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=f"Opensea {constants.NFT_NAME} #{id}",
                            url=f"https://opensea.io/assets/{constants.CHAIN}/{constants.NFT_ADDRESS}/{id}",
                        )
                    ],
                ]
            ),
        )


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA == "None":
        await update.message.reply_photo(
            photo=tools.get_logo(),
            caption=f"*{constants.PROJECT_NAME} Price*\n\nComing Soon!\n\n",
            parse_mode="Markdown",
        )
        return
    info = dextools.get_token_info(constants.CA)
    mcap = info["mcap"]
    holders = info["holders"]
    price, price_change = dextools.get_price(constants.CA)
    if price:
        price = price
    else:
        price = "N/A"
    volume = float(dextools.get_volume(constants.PAIR))
    if volume == "0.0":
        volume = "N/A"
    else:
        volume = "${:,.0f}".format(volume)
    if mcap:
        formatted_mcap = "${:,.0f}".format(mcap)
    else:
        formatted_mcap = "N/A"
    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Token Info*\n\n"
        f"Price: {price}\n"
        f"Market Cap: {formatted_mcap}\n"
        f"24 Hour Volume: {volume}\n"
        f"Holders: {holders}\n\n"
        f"{price_change}\n\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Chart", url=f"{constants.CHART_LINK}{constants.CA}"
                    )
                ],
            ]
        ),
    )


async def tax(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if constants.CA == "None":
        await update.message.reply_photo(
            photo=tools.get_logo(),
            caption=f"*{constants.PROJECT_NAME} Tax*\n\nComing Soon!\n\n",
            parse_mode="Markdown",
        )
        return
    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Tax*\n\n{constants.TAX}\n\n",
        parse_mode="Markdown",
    )


async def treasury(update: Update, context: ContextTypes.DEFAULT_TYPE):
    native_price = etherscan.get_native_price(constants.CHAIN_NATIVE.lower())
    eth_raw = etherscan.get_native_balance(constants.TREASURY)
    eth = round(float(eth_raw), 2)
    eth_dollar = float(eth) * float(native_price)
    balance = etherscan.get_token_balance(
        constants.TREASURY, constants.CA, constants.DECIMALS
    )
    price, _ = dextools.get_price(constants.CA)
    if price:
        price = price
    else:
        price = 0
    token_dollar = float(balance) * float(price)
    percent = round(balance / constants.SUPPLY * 100, 2)
    total = token_dollar + eth_dollar
    txs = etherscan.get_daily_tx_count(constants.TREASURY)

    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Treasury*\n\n"
        f"{txs} tx's in the last 24 hours\n\n"
        f"{eth} {constants.CHAIN_NATIVE.upper()} (${'{:0,.0f}'.format(eth_dollar)})\n"
        f"{balance:,.0f} {constants.TICKER} {percent}% (${'{:0,.0f}'.format(token_dollar)})\n\n"
        f"Total: ${total:,.0f}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Wallet Link",
                        url=f"{constants.SCAN_ADDRESS}/address/{constants.TREASURY}",
                    )
                ],
            ]
        ),
    )


async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) >= 1:
        if constants.CA == "None":
            await update.message.reply_photo(
                photo=tools.get_logo(),
                caption=f"*{constants.PROJECT_NAME} Wallet Info*\n\nComing Soon!\n\n",
                parse_mode="Markdown",
            )
            return
    if len(context.args) == 0:
        await update.message.reply_text("Please use /wallet [wallet_address]")
        return
    wallet = context.args[0]
    if not wallet.startswith("0x"):
        await update.message.reply_text("Please use /wallet [wallet_address]")
        return
    native_price = etherscan.get_native_price(constants.CHAIN_NATIVE.lower())
    eth = etherscan.get_native_balance(wallet, constants.CHAIN)
    eth_dollar = float(eth) * float(native_price)
    balance = etherscan.get_token_balance(wallet, constants.CA, constants.DECIMALS)
    price, _ = dextools.get_price(constants.CA)
    if price:
        price = price
    else:
        price = 0
    token_dollar = float(balance) * float(price)
    percent = round(balance / constants.SUPPLY * 100, 2)
    txs = etherscan.get_daily_tx_count(wallet)
    await update.message.reply_photo(
        photo=tools.get_logo(),
        caption=f"*{constants.PROJECT_NAME} Wallet Info*\n\n"
        f"`{wallet}`\n\n"
        f"{float(eth):.3f} {constants.CHAIN_NATIVE.upper()} (${'{:0,.0f}'.format(eth_dollar)})\n"
        f"{balance:,.0f} {constants.TICKER} {percent}% (${'{:0,.0f}'.format(token_dollar)})\n\n"
        f"{txs} tx's in the last 24 hours\n\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Wallet Link",
                        url=f"{constants.SCAN_ADDRESS}/address/{wallet}",
                    )
                ],
            ]
        ),
    )


async def twitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.get_logo(),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"@{constants.TWITTER}",
                        url=f"https://twitter.com/{constants.TWITTER}",
                    )
                ],
            ]
        ),
    )


async def website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=tools.get_logo(),
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
