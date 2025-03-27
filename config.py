import os
from typing import List, Dict

from dotenv import load_dotenv

from models import Proxy

load_dotenv()

PROXIES = []
current_proxy_index = 0


class Config:
    HEADLESS = int(os.getenv("HEADLESS").strip())
    MAX_BROWSERS = int(os.getenv("MAX_BROWSERS").strip())
    MAX_ASYNC_THREADS = int(os.getenv("MAX_ASYNC_THREADS").strip())
    USER_AGENT = os.getenv("USER_AGENT").strip()
