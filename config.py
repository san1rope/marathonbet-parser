import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROXIES = []
current_proxy_index = 0


class Config:
    HEADLESS = int(os.getenv("HEADLESS").strip())
    MAX_BROWSERS = int(os.getenv("MAX_BROWSERS").strip())
    MAX_ASYNC_THREADS = int(os.getenv("MAX_ASYNC_THREADS").strip())
    USER_AGENT = os.getenv("USER_AGENT").strip()

    FILEPATH_VERIFIED_PROXIES_FOOTBALL = Path(os.path.abspath("verified_proxies/football.json"))
    FILEPATH_VERIFIED_PROXIES_TENNIS = Path(os.path.abspath("verified_proxies/tennis.json"))
