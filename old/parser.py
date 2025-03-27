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


async def get_data_from_pages(cookies_data: Tuple[List], page_start: int, step: int):
    current_proxy_id = 0
    proxy, cookie = cookies_data[current_proxy_id]

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

    for page in range(page_start, 100, step):
        page_url = f"https://www.marathonbet.com/su/betting/Football?page={page}"
        async with session.get(url=page_url, **request_default_kwargs) as response:
            soup_page = BeautifulSoup(await response.text(), "lxml")
            logger.info(f"Сделал запрос к странице: {page_url}")

        events_on_page = soup_page.find_all(class_="event-grid")
        for event in events_on_page:
            event_url = f"https://www.marathonbet.com" + event.find(class_="member-link").get("href")
            async with session.get(url=event_url, **request_default_kwargs) as response:
                soup_event = BeautifulSoup(await response.text(), "lxml")
                logger.info(f"Сделал запрос к ивенту: {event_url}")

                # totals
                totals_list = soup_event.find("div", {"data-preference-id": re.compile("MATCH_TOTALS_SEVERAL_-")}
                                              ).find_all("tr", {"data-mutable-id": re.compile("MG1_-")})
                totals_values = {}
                flag = False
                for total_pair in totals_list[1:]:
                    te = total_pair.find_all(class_=re.compile("coeff-link-2way"))
                    if len(te) == 0:
                        if flag:
                            odd_and_even_values = total_pair.find_all("span")
                            odd_value = odd_and_even_values[0].text.strip()
                            even_value = odd_and_even_values[1].text.strip()

                            totals_values.update({
                                totals_list.index(total_pair): {"odd": odd_value, "even": even_value}
                            })

                        else:
                            odd_el = total_pair.find("th", {"data-mutable-id": re.compile("ODD_Total_Goals")})
                            if odd_el:
                                flag = True

                        continue

                    coeff_less_value = te[0].find(class_="coeff-value").text.strip()
                    coeff_less_price = te[0].find(class_="coeff-price").text.strip()
                    coeff_more_value = te[1].find(class_="coeff-value").text.strip()
                    coeff_more_price = te[1].find(class_="coeff-price").text.strip()

                    totals_values.update({
                        totals_list.index(total_pair): {
                            "less": coeff_less_value + " " + coeff_less_price,
                            "more": coeff_more_value + " " + coeff_more_price
                        }
                    })
                    print(f"totals_values = {totals_values}")


async def new_task(cookies_pairs: Tuple[Dict[Proxy, str]]):
    logging.basicConfig(
        level=logging.INFO, format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    logger.info(f"Задача запущена!")

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
