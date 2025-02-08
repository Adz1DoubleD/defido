from datetime import datetime
import random, requests

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


def get_fact():
    response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
    quote = response.json()
    return quote["text"]


def get_logo():
    random_logo = random.choice(images.logos)
    return random_logo


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


def timestamp_to_datetime(timestamp):
    try:
        datetime_obj = datetime.fromtimestamp(timestamp)
        datetime_str = datetime_obj.strftime("%Y-%m-%d %H:%M")
        return datetime_str
    except ValueError:
        return "Invalid timestamp."
