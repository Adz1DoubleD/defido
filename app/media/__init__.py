from pathlib import Path


def media_path(filename):
    return Path(__file__).resolve().parent / filename
