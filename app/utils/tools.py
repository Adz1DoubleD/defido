import aiohttp
import os
import random
import socket
from datetime import datetime

from bot.commands import custom, project, utility
from media import images


def duration_days(duration):
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes = (remainder % 3600) // 60
    return days, hours, minutes


def duration_days_timestamp(timestamp):
    current_time = datetime.utcnow()
    duration = datetime.utcfromtimestamp(timestamp) - current_time
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes = (remainder % 3600) // 60
    return days, hours, minutes


def escape_markdown(text):
    characters_to_escape = ["*", "_", "`"]
    for char in characters_to_escape:
        text = text.replace(char, "\\" + char)
    return text


async def get_fact():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://uselessfacts.jsph.pl/api/v2/facts/random"
        ) as response:
            if response.status == 200:
                quote = await response.json()
                return quote["text"]
            return "Failed to get a random fact."


def get_logo():
    random_logo = random.choice(images.logos)
    return random_logo


async def get_today():
    now = datetime.now()
    url = f"https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all/{now.month}/{now.day}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()

                if (
                    "selected" in data
                    and isinstance(data["selected"], list)
                    and len(data["selected"]) > 0
                ):
                    random_event = random.choice(data["selected"])

                    event_text = random_event.get("text", "No description available.")
                    year = random_event.get("year", "Unknown Year")

                    event_pages = random_event.get("pages", [])
                    wiki_url = (
                        event_pages[0]["content_urls"]["desktop"]["page"]
                        if event_pages
                        else "No link available."
                    )

                    return f"📅 *{year}*: {event_text}\n🔗 [Read more]({wiki_url})"

            return "⚠️ No historical events found for today."


async def get_word(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()

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
            return None, None


def is_local():
    ip = socket.gethostbyname(socket.gethostname())
    return ip.startswith("127.") or ip.startswith("192.168.") or ip == "localhost"


def timestamp_to_datetime(timestamp):
    try:
        datetime_obj = datetime.fromtimestamp(timestamp)
        datetime_str = datetime_obj.strftime("%Y-%m-%d %H:%M")
        return datetime_str
    except ValueError:
        return "Invalid timestamp."


async def update_bot_commands():
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/setMyCommands"

    all_commands = [
        {
            "command": cmd[0] if isinstance(cmd, list) else cmd,
            "description": desc,
        }
        for handlers in [custom.HANDLERS, project.HANDLERS, utility.HANDLERS]
        for cmd, _, desc in handlers
    ]

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json={"commands": all_commands, "scope": {"type": "default"}}
        ) as response:
            if response.status == 200:
                return "✅ Commands updated successfully."
            else:
                response_text = await response.text()
                return f"⚠️ Failed to update bot commands: {response_text}"
