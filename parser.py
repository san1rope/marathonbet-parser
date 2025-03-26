import logging
import asyncio
import re
import os
from multiprocessing import Queue
from typing import Dict, List, Tuple

from aiohttp import BasicAuth, ClientSession
from bs4 import BeautifulSoup

from config import Config
from models import Proxy
from utils import Utils as Ut

logger = logging.getLogger(__name__)


async def get_data_from_pages(cookies_data: Dict[Proxy, str], page_start: int, page_end: int):
    pass


async def new_task(cookies_pairs: Tuple[Dict[Proxy, str]]):
    logging.basicConfig(
        level=logging.INFO, format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    logger.info(f"Задача запущена!")

    print(f"cookies_pairs = {cookies_pairs}")

    # proxy_ip = f"http://{proxy.host}:{proxy.port}"
    # proxy_auth = BasicAuth(login=proxy.username, password=proxy.password)
    #
    # url = "https://www.marathonbet.com/su/betting/Football?page="
    # headers = {
    #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    #     "accept-encoding": "gzip, deflate, br, zstd",
    #     "accept-language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
    #     "cookie": f"cf_clearance={cookie}",
    #     "priority": "u=0, i",
    #     "referer": "https://www.marathonbet.com/su/?cppcids=all",
    #     "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Opera GX";v="117"',
    #     "sec-ch-ua-mobile": '?0',
    #     "sec-ch-ua-platform": '"Windows"',
    #     "sec-fetch-dest": 'document',
    #     "sec-fetch-mode": 'navigate',
    #     "sec-fetch-site": "same-origin",
    #     "sec-fetch-user": "?1",
    #     "upgrade-insecure-requests": "1",
    #     "user-agent": Config.USER_AGENT
    # }
    #
    # request_default_kwargs = {"headers": headers, "proxy": proxy_ip, "proxy_auth": proxy_auth, "timeout": 20}
    # session = ClientSession()
