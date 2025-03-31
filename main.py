import asyncio
import logging
from multiprocessing import Process, Queue
from concurrent.futures.process import ProcessPoolExecutor
from queue import Empty

from aiohttp import BasicAuth, ClientSession
from bs4 import BeautifulSoup

from config import Config, PROXIES
from models import Proxy
from parser import start_parser
from utils import Utils as Ut, Utils

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO, format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    logging.getLogger("WDM").setLevel(logging.CRITICAL)
    logger.info("Запускаю софт...")

    load_proxies = await Ut.load_proxy_from_file()
    with (ProcessPoolExecutor(max_workers=Config.MAX_BROWSERS) as executor):
        futures = [executor.submit(Ut.wrapper, Ut.verify_browser, proxy) for proxy in load_proxies]
        for future in futures:
            result = future.result()
            if result:
                PROXIES.append(result)

    queue_proxy = Queue()
    queue_football = Queue()
    queue_tennis = Queue()

    proxies_for_process = int(len(PROXIES) / 2)
    Process(target=Ut.wrapper, args=(start_parser, PROXIES[:proxies_for_process], Ut.FOOTBALL, queue_football,
                                     queue_proxy,)).start()
    Process(target=Ut.wrapper, args=(start_parser, PROXIES[proxies_for_process:], Ut.TENNIS, queue_tennis,
                                     queue_proxy,)).start()

    football_leagues_urls = None
    tennis_leagues_urls = None
    session = ClientSession()
    while True:
        await asyncio.sleep(0.05)
        try:
            msg = queue_football.get_nowait()
            print(f"new_message football = {msg}")

        except Empty:
            try:
                msg = queue_tennis.get_nowait()
                print(f"new_message tennis = {msg}")

            except Empty:
                continue

        if msg.get("type") == "get_markup_live_page":
            if msg.get("game_name") == Ut.FOOTBALL and football_leagues_urls:
                queue_football.put({"type": Utils.FOOTBALL, "value": football_leagues_urls})
                await asyncio.sleep(0.5)
                football_leagues_urls = None
                print("send markup to football from if")
                continue

            elif msg.get("game_name") == Ut.TENNIS and tennis_leagues_urls:
                queue_tennis.put({"type": Utils.TENNIS, "value": tennis_leagues_urls})
                await asyncio.sleep(0.5)
                tennis_leagues_urls = None
                print("send markup to tennis from if")
                continue

            proxy = Proxy(**msg["proxy"])
            proxy_ip = f"http://{proxy.host}:{proxy.port}"
            proxy_auth = BasicAuth(login=proxy.username, password=proxy.password)
            async with session.get(url="https://www.marathonbet.com/en/live/", headers=msg["headers"], proxy=proxy_ip,
                                   proxy_auth=proxy_auth, timeout=20) as response:
                markup = await response.text()
                soup = BeautifulSoup(markup, "lxml")

            events_container = soup.find("div", {"data-id": "container_EVENTS"})
            football_leagues = events_container.find(
                "div", {"class": "sport-category-container", "data-sport-treeid": "26418"}).find(
                class_="sport-category-content").find_all("a", {"class": "category-label-link"})
            tennis_leagues = events_container.find(
                "div", {"class": "sport-category-container", "data-sport-treeid": "22723"}).find(
                class_="sport-category-content").find_all("a", {"class": "category-label-link"})

            football_leagues_urls = ["https://www.marathonbet.com" + el["href"] for el in football_leagues]
            tennis_leagues_urls = ["https://www.marathonbet.com" + el["href"] for el in tennis_leagues]

            if msg.get("game_name") == Utils.FOOTBALL:
                queue_football.put({"type": Utils.FOOTBALL, "value": football_leagues_urls})
                await asyncio.sleep(0.5)
                print("send football")

            elif msg.get("game_name") == Utils.TENNIS:
                queue_tennis.put({"type": Utils.TENNIS, "value": tennis_leagues_urls})
                await asyncio.sleep(0.5)
                print("send tennis")


if __name__ == '__main__':
    asyncio.run(main())
