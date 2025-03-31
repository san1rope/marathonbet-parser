import json
import logging
import os
from multiprocessing import Queue

from config import Config
from models import Proxy
from utils import Utils as Ut

logger = logging.getLogger(__name__)


async def proxy_verify_process(queue: Queue):
    logging.basicConfig(
        level=logging.INFO, format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    logging.getLogger("WDM").setLevel(logging.CRITICAL)
    logging.getLogger("uc").setLevel(logging.CRITICAL)

    while True:
        msg = queue.get()

        host, port, username, password = msg["proxy"].split(":")
        proxy = Proxy(host=host, port=int(port), username=username, password=password)

        result = await Ut.verify_browser(proxy=proxy)
        if result is None:
            logger.warning(f"{proxy} | Не удалось пройти проверку браузера!")
            continue

        proxy, cookie = result

        if msg["game"] == Ut.FOOTBALL:
            path_obj = Config.FILEPATH_VERIFIED_PROXIES_FOOTBALL

        elif msg["game"] == Ut.TENNIS:
            path_obj = Config.FILEPATH_VERIFIED_PROXIES_TENNIS

        else:
            continue

        path_obj.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path_obj.open("r", encoding="utf-8") as file:
                verified_proxies_obj = json.load(file)

        except FileNotFoundError:
            verified_proxies_obj = {}

        verified_proxies_obj[str(proxy)] = cookie
        with path_obj.open("w", encoding="utf-8") as file:
            json.dump(verified_proxies_obj, file, indent=4, ensure_ascii=False)

        logger.info(f"{proxy} | Прокси прошло проверку! {msg['game']}")
