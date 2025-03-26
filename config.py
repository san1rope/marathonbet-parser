import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    HEADLESS = int(os.getenv("HEADLESS").strip())
    MAX_PROCESSES = int(os.getenv("MAX_PROCESSES").strip())
    USER_AGENT = os.getenv("USER_AGENT").strip()
