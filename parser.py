import json
import logging
import asyncio
from time import time
from asyncio import Semaphore
from queue import Empty
from typing import List, Dict
from multiprocessing import Queue

from aiohttp import BasicAuth, ClientSession
from bs4 import BeautifulSoup

from config import PROXIES, Config
from utils import Utils as Ut, current_proxy_index

logger = logging.getLogger(__name__)


async def parse_leagues(session: ClientSession, request_default_kwargs: Dict, leagues_urls: List[str], parse_method):
    for league_url in leagues_urls:
        async with session.get(url=league_url, **request_default_kwargs) as response:
            markup_league = await response.text()
            soup_league = BeautifulSoup(markup_league, "lxml")

        events_elements = soup_league.find_all("div", class_="coupon-row")
        if len(events_elements) == 1:
            out_data = await parse_method(soup=events_elements[0])
            print(out_data)

            for event_el in events_elements:
                event_url = f"https://www.marathonbet.com/en/live/{event_el['data-event-treeid']}"
                async with session.get(url=event_url, **request_default_kwargs) as response:
                    event_markup = await response.text()
                    soup_event = BeautifulSoup(event_markup, "lxml")

                out_data = await parse_method(soup=soup_event)
                print(out_data)


async def start_parser(proxies: List, game_name: str, queue: Queue, queue_proxy: Queue):
    logging.basicConfig(
        level=logging.INFO, format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    logger.info(f"Запустил парсер по {game_name}")

    if game_name == Ut.FOOTBALL:
        parse_method = Ut().parse_data_from_event_football

    elif game_name == Ut.TENNIS:
        parse_method = Ut().parse_data_from_event_tennis

    else:
        return

    PROXIES.extend(proxies)
    proxy, cookie = await Ut.get_next_proxy(current_proxy_index=current_proxy_index)

    proxy_ip = f"http://{proxy.host}:{proxy.port}"
    proxy_auth = BasicAuth(login=proxy.username, password=proxy.password)
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
        "cookie": f"cf_clearance={cookie}",
        "priority": "u=0, i",
        "referer": "https://www.marathonbet.com/su/?cppcids=all",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Opera GX";v="117"',
        "sec-ch-ua-mobile": '?0',
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": 'document',
        "sec-fetch-mode": 'navigate',
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": Config.USER_AGENT
    }
    request_default_kwargs = {"headers": headers, "proxy": proxy_ip, "proxy_auth": proxy_auth, "timeout": 20}
    session = ClientSession()
    while True:
        queue.put({"type": "get_markup_live_page", "game_name": game_name, "proxy": proxy.dict(), "headers": headers})
        await asyncio.sleep(0.5)
        print("message has been sent")

        leagues_urls = None
        while True:
            try:
                msg = queue.get_nowait()
                print(f"new_message parser = {msg}")

            except Empty:
                continue

            if msg.get("type") == game_name:
                leagues_urls = msg["value"]
                break

        distribut_urls = [[] for _ in range(Config.MAX_ASYNC_THREADS)]
        dp_index = 0
        for item in leagues_urls:
            distribut_urls[dp_index].append(item)
            dp_index += 1

            if dp_index >= len(distribut_urls):
                dp_index = 0

        semaphore = Semaphore(Config.MAX_ASYNC_THREADS)
        tasks = [Ut.worker(
            semaphore=semaphore, func=parse_leagues, session=session, request_default_kwargs=request_default_kwargs,
            leagues_urls=urls, parse_method=parse_method
        ) for urls in distribut_urls]
        start_time = time()
        result = await asyncio.gather(*tasks)
        result_time = time() - start_time
        print(f"FINISH TIME: {result_time}")

        if game_name == Ut.FOOTBALL:
            path_obj = Config.FILEPATH_VERIFIED_PROXIES_FOOTBALL

        elif game_name == Ut.TENNIS:
            path_obj = Config.FILEPATH_VERIFIED_PROXIES_TENNIS

        else:
            continue

        try:
            with path_obj.open("r", encoding="utf-8") as file:
                verified_proxies = json.load(file)

        except FileNotFoundError:
            verified_proxies = {}

        for proxy, cookie in verified_proxies.items():
            PROXIES.append([proxy, cookie])

        with path_obj.open("w", encoding="utf-8") as file:
            json.dump({}, file, indent=4, ensure_ascii=False)
