
from telegram import *
from telegram.ext import *

from data import constants
from media import index as media
from data import api

from datetime import datetime
from pyfiglet import Figlet
from gtts import gTTS
import time as t
import requests
import random
import pytz
import re


async def ascii(update: Update, context: ContextTypes.DEFAULT_TYPE):
    input_text = " ".join(context.args).upper()
    if input_text == "":
        await update.message.reply_text(
            f"Please follow the command with the word you want to use",
        parse_mode="Markdown",
        )
    else:
        words = input_text.split()
        input_text = "\n".join(words)
        custom_fig = Figlet(font="slant")
        ascii_art = custom_fig.renderText(input_text)
        await update.message.reply_text(
            f"*{constants.PROJECT_NAME} ASCII Art*\n\n"
            f"Best viewed on PC full screen.\n\n`{ascii_art}`",
        parse_mode="Markdown",
        )


async def blocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time = round(t.time())
    blocks_time = api.get_block(constants.CHAIN, time)
    await update.message.reply_photo(
        photo = media.logo(),
        caption =
            f"*Latest {constants.CHAIN.upper()} Block *\n\n"
            f"{blocks_time}\n\n",
        parse_mode="Markdown"
    )


async def bridge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo = media.logo(),
        caption=
            f"*{constants.PROJECT_NAME} BASE Bridge*\n\nThese are a few options to obtain Base ETH\n\n"
            "- [Official Base Bridge](https://bridge.base.org/deposit)\n\n"
            "3rd Party Bridges:\n\n"
            "- [HoudiniSwap](http://www.houdiniswap.com/)\n"
            "- [Synapse Protocol](https://synapseprotocol.com/?fromChainId=1&toChainId=8453)\n",
        parse_mode="Markdown"
        )
    


async def check_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Please provide exactly 2 inputs to compare.")
        return
    else:
        first = context.args[0]
        second = context.args[1]

        if first == second:
            reply = "✅ Both inputs match"
        else:
            reply = "❌ Inputs do not match"

        await update.message.reply_photo(
            photo = media.logo(),
            caption =
                f"*{constants.PROJECT_NAME} Input Checker*\n\n"
                f"First:\n{first}\n\n"
                f"Second:\n{second}\n\n"
                f"{reply}\n\n",
            parse_mode="Markdown"
            )


async def coinflip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = user.username or f"{user.first_name} {user.last_name}"
    choose = ["Heads", "Tails"]
    choice = random.choice(choose)
    await update.message.reply_photo(
        photo = media.logo(),
        caption =
            f"*{constants.PROJECT_NAME} Input Checker*\n\n{api.escape_markdown(user_info)} flipped {choice}\n\n",
        parse_mode="Markdown"
)


async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo = media.logo(),
        caption =
            f"*{constants.PROJECT_NAME} Fact!*\n\n{api.get_fact()}\n\n",
        parse_mode="Markdown"
        )


async def fg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fear_response = requests.get("https://api.alternative.me/fng/?limit=0")
    fear_data = fear_response.json()
    fear_values = []
    for i in range(7):
        timestamp = float(fear_data["data"][i]["timestamp"])
        localtime = datetime.fromtimestamp(timestamp)
        fear_values.append(
            (
                fear_data["data"][i]["value"],
                fear_data["data"][i]["value_classification"],
                localtime,
            )
        )
    duration_in_s = float(fear_data["data"][0]["time_until_update"])
    days, remainder = divmod(duration_in_s, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    caption = "*Market Fear and Greed Index*\n\n"
    caption += f'{fear_values[0][0]} - {fear_values[0][1]} - {fear_values[0][2].strftime("%A %B %d")}\n\n'
    caption += "Change:\n"
    for i in range(1, 7):
        caption += f'{fear_values[i][0]} - {fear_values[i][1]} - {fear_values[i][2].strftime("%A %B %d")}\n'
    caption += "\nNext Update:\n"
    caption += f"{int(hours)} hours and {int(minutes)} minutes"
    await update.message.reply_photo(
        photo="https://alternative.me/crypto/fear-and-greed-index.png",
        caption=caption,
        parse_mode="Markdown"
        )


async def gas(update: Update, context: ContextTypes.DEFAULT_TYPE):
        gas_data = api.get_gas("eth")
        await update.message.reply_photo(
            photo = media.logo(),
            caption=
                f"*{constants.CHAIN.upper()} Gas Prices:*\n\n"
                f'Low: {gas_data["result"]["SafeGasPrice"]} Gwei\n'
                f'Average: {gas_data["result"]["ProposeGasPrice"]} Gwei\n'
                f'High: {gas_data["result"]["FastGasPrice"]} Gwei\n\n',
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text=f"{constants.CHAIN.upper()} Gas Tracker", url="https://etherscan.io/gastracker")]]
            ),
        )


async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke_response = requests.get("https://v2.jokeapi.dev/joke/Any?safe-mode")
    joke = joke_response.json()
    if joke["type"] == "single":
        await update.message.reply_photo(
        photo = media.logo(),
        caption =
            f'{constants.PROJECT_NAME} Joke\n\n'
            f'{joke["joke"]}\n\n',
        parse_mode="Markdown"
        )
    else:
        await update.message.reply_photo(
        photo = media.logo(),
        caption =
            f'{constants.PROJECT_NAME} Joke\n\n'
            f'{joke["setup"]}\n\n{joke["delivery"]}\n\n',
        parse_mode="Markdown"
        )


async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo = media.logo(),
        caption=
            f"*{constants.PROJECT_NAME} Quote*\n\n"f"{api.get_quote()}",
        parse_mode="Markdown",
    )


async def roll(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text('Please follow the command with a maximum number for the roll')
        return
    else:
        max_number_str = context.args[0]
        if not max_number_str.isdigit():
            await update.message.reply_text('Please follow the command with a maximum number for the roll')

        max_number = int(max_number_str)
        if max_number < 2:
            await update.message.reply_text('Please follow the command with a maximum number for the roll')
            return
        
        user = update.effective_user
        user_info = user.username or f"{user.first_name} {user.last_name}"
        max_number = int(context.args[0])
        result = random.randint(1, max_number)
        await update.message.reply_photo(
        photo = media.logo(),
        caption=
            f'*{constants.PROJECT_NAME} Number Roll*\n\n{api.escape_markdown(user_info)} rolled {result}\n\nBetween 1 and {max_number}\n\n',
        parse_mode="Markdown",)


async def say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide some words to convert to speech.")
        return
    voice_note = gTTS(" ".join(context.args), lang='en', slow=False)
    voice_note.save("media/voicenote.mp3")
    await update.message.reply_audio(audio=open("media/voicenote.mp3", "rb"))


async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.split(" ")
    timezones = [
        ("America/Los_Angeles", "PST"),
        ("America/New_York", "EST"),
        ("UTC", "UTC"),
        ("Europe/Dublin", "IST"),
        ("Europe/London", "GMT"),
        ("Europe/Berlin", "CET"),
        ("Asia/Dubai", "GST"),
        ("Asia/Tokyo", "JST"),
        ("Australia/Sydney", "AEST"),
    ]
    current_time = datetime.now(pytz.timezone("UTC"))
    local_time = current_time.astimezone(pytz.timezone("UTC"))
    try:
        if len(message) > 1:
            time_variable = message[1]
            time_format = "%I%p"
            if re.match(r"\d{1,2}:\d{2}([ap]m)?", time_variable):
                time_format = (
                    "%I:%M%p"
                    if re.match(r"\d{1,2}:\d{2}am", time_variable, re.IGNORECASE)
                    else "%I:%M%p"
                )
            input_time = datetime.strptime(time_variable, time_format).replace(
                year=local_time.year, month=local_time.month, day=local_time.day
            )
            if len(message) > 2:
                time_zone = message[2]
                for tz, tz_name in timezones:
                    if time_zone.lower() == tz_name.lower():
                        tz_time = pytz.timezone(tz).localize(input_time)
                        time_info = f"{input_time.strftime('%A %B %d %Y')}\n"
                        time_info += f"{input_time.strftime('%I:%M %p')} - {time_zone.upper()}\n\n"
                        for tz_inner, tz_name_inner in timezones:
                            converted_time = tz_time.astimezone(pytz.timezone(tz_inner))
                            time_info += f"{converted_time.strftime('%I:%M %p')} - {tz_name_inner}\n"
                        await update.message.reply_photo(
                            photo = media.logo(),
                            caption =
                                f"*{constants.PROJECT_NAME} World Time*\n\n"
                                f"{time_info}\n\n",
                            parse_mode="Markdown")
                        return
            time_info = f"{input_time.strftime('%A %B %d %Y')}\n"
            time_info += (
                f"{input_time.strftime('%I:%M %p')} - {time_variable.upper()}\n\n"
            )
            for tz, tz_name in timezones:
                tz_time = input_time.astimezone(pytz.timezone(tz))
                time_info += f"{tz_time.strftime('%I:%M %p')} - {tz_name}\n"
            await update.message.reply_photo(
                photo = media.logo(),
                caption =
                    f"*{constants.PROJECT_NAME} World Time*\n\n"
                    f"{time_info}",
                parse_mode="Markdown")
            return
        time_info = f"{local_time.strftime('%A %B %d %Y')}\n"
        time_info += (
            f"{local_time.strftime('%I:%M %p')} - {local_time.strftime('%Z')}\n\n"
        )
        for tz, tz_name in timezones:
            tz_time = local_time.astimezone(pytz.timezone(tz))
            time_info += f"{tz_time.strftime('%I:%M %p')} - {tz_name}\n"
        await update.message.reply_photo(
            photo = media.logo(),
            caption =
                f"*{constants.PROJECT_NAME} World Time*\n\n"
                f"{time_info}\n\n",
            parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(
            "use `/time HH:MMPM or HHAM TZ`", parse_mode="Markdown"
        )


async def timestamp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = " ".join(context.args)
        if text == "":
            await update.message.reply_text(
                "Please follow the command with the timestamp you wish to convert"
            )
        else:
            stamp = int(" ".join(context.args).lower())
            time = api.timestamp_to_datetime(stamp)
            current_time = datetime.utcnow()
            timestamp_time = datetime.utcfromtimestamp(stamp)
            time_difference = current_time - timestamp_time
            if time_difference.total_seconds() > 0:
                time_message = "ago"
            else:
                time_message = "away"
                time_difference = abs(time_difference)
            years = time_difference.days // 365
            months = (time_difference.days % 365) // 30
            days = time_difference.days % 30
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes = remainder // 60
            await update.message.reply_photo(
                photo = media.logo(),
                caption= f"*{constants.PROJECT_NAME} Timestamp Conversion*\n\n"
                        f"{stamp}\n{time} UTC\n\n"
                        f"{years} years, {months} months, {days} days, "
                        f"{hours} hours, {minutes} minutes {time_message}\n\n",
                parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(
            "Timestamp not recognised"
        )


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = api.get_today()
    today = random.choice(data["data"]["Events"])
    await update.message.reply_photo(
        photo = media.logo(),
        caption=
            f'*{constants.PROJECT_NAME} OTD*\n\nOn this day in {today["year"]}:\n\n{today["text"]}\n\n',
        parse_mode="Markdown")


async def wei(update: Update, context: ContextTypes.DEFAULT_TYPE):
    eth = " ".join(context.args)
    if eth == "":
        await update.message.reply_text("Please follow the command with the amount of currency you wish to convert")
    else:
        wei = int(float(eth) * 10**18)
        await update.message.reply_photo(
        photo = media.logo(),
        caption =
            f"*{constants.PROJECT_NAME} WEI Convertor*\n\n{eth} is equal to \n" f"`{wei}` wei\n\n",
        parse_mode="Markdown")


async def word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        word = " ".join(context.args).lower()
        if word == "":
            await update.message.reply_text(
                f"Please use /word followed by the word you want to search")
            return
        
        definition, audio_url = api.get_word(word)
        caption = (
            f"*{constants.PROJECT_NAME} Dictionary*\n\n{word}:\n\n{definition}"
        )
        keyboard_markup = None
        
        if audio_url:
            keyboard_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Pronunciation", url=f"{audio_url}")]]
            )
        
        await update.message.reply_photo(
        photo = media.logo(),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=keyboard_markup,
        )
    except Exception as e:
        await update.message.reply_text("Word not found")